import datetime
from typing import List, Union

from fastapi import FastAPI, Depends, Response
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, relationship
from sqlalchemy.orm import sessionmaker, declarative_base
from starlette.responses import JSONResponse

from models.request_schemas import CreateRequest, ItemRequest, WeekdayModel, ActionTypeModel, MultiItemRequest
from models.response_schemas import ItemResponse, MessageResponse
from models.response_schemas import RESPONSE_404
from models.response_schemas import TransactionResponse, TransactionItemResponse

DATABASE_URL = 'sqlite:///inventory.db'
engine = create_engine(DATABASE_URL, echo=True)  # echo=True logs SQL queries
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

app = FastAPI(root_path='/dev')


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    stock = Column(Integer, default=0)
    max_checkout = Column(Integer)


class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    action = Column(String, nullable=False)  # 'checkout' or 'restock'
    timestamp = Column(DateTime, default=func.now())
    day_of_week = Column(String,
                         default=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][
                             datetime.datetime.today().weekday()])
    student_id = Column(String, nullable=True)

    entries = relationship('TransactionItem', back_populates='transaction', cascade='all, delete-orphan')


class TransactionItem(Base):
    __tablename__ = 'transaction_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(Integer, ForeignKey('transactions.id'), nullable=False)
    item_name = Column(String, ForeignKey('items.name'), nullable=False)
    item_quantity = Column(Integer, nullable=False)

    transaction = relationship('Transaction', back_populates='entries')


Base.metadata.create_all(engine)


@app.delete('/delete_all', response_model=MessageResponse)
def delete_all_items(db: Session = Depends(get_db)):
    """Delete all items from the inventory and clears all logs."""
    db.query(Item).delete()
    db.query(TransactionItem).delete()
    db.commit()
    return MessageResponse(message='All items have been deleted.')


@app.get('/items', response_model=list[ItemResponse], responses={
    200: {
        'description': 'All items in inventory',
        'content': {
            'application/json': {
                'example': [
                    {'name': 'bar', 'stock': 10, 'max_checkout': 10},
                    {'name': 'foo', 'stock': 1, 'max_checkout': 10},
                    {'name': 'baz', 'stock': 0, 'max_checkout': 10},
                ]
            }
        }
    }
})
def get_items(db: Session = Depends(get_db)) -> list[ItemResponse]:
    """Fetch all items in inventory."""
    return [ItemResponse(id=row.id, name=row.name, stock=row.stock, max_checkout=row.max_checkout)
            for row in db.query(Item).all()]


@app.get('/items/{item_name}', response_model=ItemResponse, responses={
    200: {
        'description': 'Item requested by name',
        'content': {
            'application/json': {
                'example': {'id': 1, 'name': 'bar', 'stock': 10, 'max_checkout': 5},
            }
        }
    },
    **RESPONSE_404
})
def get_item(item_name: str, db: Session = Depends(get_db)):
    """Gets data for a specific item in inventory"""
    item = db.query(Item).filter_by(name=item_name).first()
    if not item:
        return JSONResponse(status_code=404, content={'message': 'Item not found.'})

    return ItemResponse(id=item.id, name=item.name, stock=item.stock, max_checkout=item.max_checkout)


@app.delete('/items/{item_name}', response_model=MessageResponse, responses={
    200: {
        'model': MessageResponse,
        'description': 'Item deleted successfully',
    },
    **RESPONSE_404
})
def delete_item(item_name: str, db: Session = Depends(get_db)):
    """Deletes item from inventory"""
    item = db.query(Item).filter_by(name=item_name).first()
    if not item:
        return JSONResponse(status_code=404, content={'message': 'Item not found.'})
    db.delete(item)
    db.commit()
    return MessageResponse(message='Item deleted successfully.')


@app.post('/create', status_code=201, response_model=MessageResponse, responses={
    201: {
        'model': MessageResponse,
        'description': 'Item created successfully.'
    },
    409: {
        'model': MessageResponse,
        'description': 'Item with the given name already exists.'
    }
})
def create_item(request: CreateRequest, response: Response, db: Session = Depends(get_db)):
    """Creates a new item in the inventory"""
    if db.query(Item).filter_by(name=request.name).first():
        return JSONResponse(status_code=409, content={'message': 'Item with the given name already exists.'})

    item = Item(name=request.name, stock=request.initial_stock, max_checkout=request.max_checkout)
    db.add(item)
    db.commit()
    response.headers['Location'] = f'/items/{item.name}'
    return MessageResponse(message=f'Created item {item.name} with an initial stock of {item.stock}')


@app.post('/checkout', response_model=MessageResponse, responses={
    200: {
        'model': MessageResponse,
        'description': 'Item(s) checked out successfully.'
    },
    400: {
        'model': MessageResponse,
        'description': 'Attempted to checkout more than the maximum allowed.'
    },
    409: {
        'model': MessageResponse,
        'description': 'Not enough stock.'
    },
    **RESPONSE_404
})
def checkout_item(request: Union[ItemRequest, MultiItemRequest], db: Session = Depends(get_db)):
    """Checkout an item from inventory."""
    multi_request: MultiItemRequest
    if not isinstance(request, MultiItemRequest):
        multi_request = MultiItemRequest(student_id=request.student_id, items=[request])
    else:
        multi_request = request

    not_found = []
    insufficient_stock = []
    over_max = []
    for item_request in multi_request.items:
        item = db.query(Item).filter_by(name=item_request.name).first()

        if not item:
            not_found.append(item_request.name)
        elif item_request.quantity > item.max_checkout:
            over_max.append(item_request)
        elif item.stock < item_request.quantity:
            insufficient_stock.append(item_request.name)

    if not_found:
        return JSONResponse(status_code=404, content={'message': f'Item(s) {", ".join(not_found)} not found.'})

    if over_max:
        return JSONResponse(status_code=400, content={
            'message': f'Attempted to checkout more than the max quantity allowed for items(s) {", ".join(over_max)}.'})

    if insufficient_stock:
        return JSONResponse(status_code=409,
                            content={'message': f'Not enough stock for item(s) {", ".join(insufficient_stock)}.'})

    for item_request in multi_request.items:
        db.query(Item).filter_by(name=item_request.name).first().stock -= item_request.quantity

    log_action(db, ActionTypeModel.CHECKOUT, items=multi_request)
    db.commit()

    return MessageResponse(message='Checked out items successfully.')


@app.post('/restock', response_model=MessageResponse, responses={
    200: {
        'model': MessageResponse,
        'description': 'Item restocked successfully.'
    },
    **RESPONSE_404
})
def restock_item(request: ItemRequest, db: Session = Depends(get_db)):
    """Restock an item in inventory."""
    item = db.query(Item).filter_by(name=request.name).first()

    if item:
        item.stock += request.quantity
    else:
        return JSONResponse(status_code=404, content={'message': 'Item not found.'})

    log_action(db, action=ActionTypeModel.RESTOCK, items=MultiItemRequest(items=[request]))
    db.commit()

    return MessageResponse(message=f'Restocked {request.quantity} {request.name}(s).')


@app.get('/logs', response_model=List[TransactionResponse], responses={
    200: {
        'model': List[TransactionResponse],
        'description': 'The list of all transactions'
    }
})
def get_logs(db: Session = Depends(get_db), day_of_week: WeekdayModel | int | None = None,
             student_id: str | None = None,
             item_name: str | None = None, action: ActionTypeModel | None = None) -> list[TransactionResponse]:
    """Fetch all action logs."""
    query = db.query(Transaction)

    if day_of_week is not None:
        if isinstance(day_of_week, int):
            query = query.filter_by(
                day_of_week=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][
                    day_of_week])
        else:
            query = query.filter_by(day_of_week=day_of_week)
    if student_id is not None:
        query = query.filter_by(student_id=student_id)
    if action is not None:
        query = query.filter_by(action=action)
    if item_name is not None:
        query = query.filter(Transaction.entries.any(item_name=item_name))

    transactions = query.all()
    return [
        TransactionResponse(transaction_id=transaction.id,
                            student_id=transaction.student_id,
                            day_of_week=transaction.day_of_week,
                            action=transaction.action,
                            timestamp=transaction.timestamp,
                            items=[TransactionItemResponse(item_name=item.item_name, item_quantity=item.item_quantity)
                                   for item in transaction.entries])
        for transaction in transactions]


def log_action(db: Session, action: ActionTypeModel, items: MultiItemRequest):
    transaction = Transaction(action=action, student_id=items.student_id)
    db.add(transaction)
    db.flush()

    for item in items.items:
        db.add(TransactionItem(transaction_id=transaction.id, item_name=item.name, item_quantity=item.quantity))
