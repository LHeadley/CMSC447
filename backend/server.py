import datetime
from typing import Type, List, Union

from fastapi import FastAPI, Depends, Response
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, relationship, load_only
from sqlalchemy.orm import sessionmaker, declarative_base
from starlette.responses import JSONResponse

from request_schemas import CreateRequest, ActionRequest
from response_schemas import ItemResponse, MessageResponse
from response_schemas import RESPONSE_404
from response_schemas import TransactionResponse, TransactionItemResponse

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
    unit_weight = Column(Integer, nullable=False)  # weight/quantity per unit
    price = Column(Integer, nullable=False)  # price per unit
    stock = Column(Integer, default=0)
    supplier = Column(String)


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
    return {'message': 'All items deleted from inventory.'}


@app.get('/items', response_model=list[ItemResponse], responses={
    200: {
        'description': 'All items in inventory',
        'content': {
            'application/json': {
                'example': [
                    {'name': 'bar', 'unit_weight': 1, 'price': 100, 'stock': 10},
                    {'name': 'foo', 'unit_weight': 5, 'price': 10, 'stock': 1},
                    {'name': 'baz', 'unit_weight': 1, 'price': 50, 'stock': 0},
                ]
            }
        }
    }
})
def get_items(db: Session = Depends(get_db)) -> list[Type[Item]]:
    """Fetch all items in inventory."""
    return db.query(Item).all()


@app.get('/items/{item_name}', response_model=ItemResponse, responses={
    200: {
        'description': 'Item requested by name',
        'content': {
            'application/json': {
                'example': {'name': 'bar', 'unit_weight': 1, 'price': 100, 'stock': 10}
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

    return item


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

    item = Item(name=request.name, unit_weight=request.unit_weight, price=request.price, stock=request.initial_stock)
    db.add(item)
    db.commit()
    response.headers['Location'] = f'/items/{item.name}'
    return {'message': f'Created item {item.name} with an initial stock of {item.stock}'}


@app.post('/checkout', response_model=MessageResponse, responses={
    200: {
        'model': MessageResponse,
        'description': 'Item(s) checked out successfully.'
    },
    409: {
        'model': MessageResponse,
        'description': 'Not enough stock.'
    },
    **RESPONSE_404
})
def checkout_item(request: Union[ActionRequest, list[ActionRequest]], db: Session = Depends(get_db)):
    """Checkout an item from inventory."""
    requests: list[ActionRequest]
    if not isinstance(request, list):
        requests = [request]
    else:
        requests = request

    not_found = []
    insufficient_stock = []
    for action in requests:
        item = db.query(Item).filter_by(name=action.name).first()

        if not item:
            not_found.append(action.name)

        if item.stock < action.quantity:
            insufficient_stock.append(action.name)

    if not_found:
        return JSONResponse(status_code=404, content={'message': f'Item(s) {", ".join(not_found)} not found.'})

    if insufficient_stock:
        return JSONResponse(status_code=409,
                            content={'message': f'Not enough stock for item(s) {", ".join(insufficient_stock)}.'})

    for action in requests:
        db.query(Item).filter_by(name=action.name).first().stock -= action.quantity

    log_action(db, 'checkout', requests)
    db.commit()

    return {'message': 'Checked out items successfully.'}


@app.post('/restock', response_model=MessageResponse, responses={
    200: {
        'model': MessageResponse,
        'description': 'Item restocked successfully.'
    },
    **RESPONSE_404
})
def restock_item(request: ActionRequest, db: Session = Depends(get_db)):
    """Restock an item in inventory."""
    item = db.query(Item).filter_by(name=request.name).first()

    if item:
        item.stock += request.quantity
    else:
        return JSONResponse(status_code=404, content={'message': 'Item not found.'})

    log_action(db, 'restock', [request])
    db.commit()

    return {'message': f'Restocked {request.quantity} {request.name}(s).'}


@app.get('/logs', response_model=List[TransactionResponse], responses={
    200: {
        'model': List[TransactionResponse],
        'description': 'The list of all transactions'
    }
})
def get_logs(db: Session = Depends(get_db)) -> list[TransactionResponse]:
    """Fetch all action logs."""
    transactions = db.query(Transaction).options(load_only(
        Transaction.id,
        Transaction.student_id,
        Transaction.day_of_week,
        Transaction.action,
        Transaction.timestamp
    )).all()
    return [
        TransactionResponse(transaction_id=getattr(transaction, "id"),
                            student_id=getattr(transaction, "student_id"),
                            day_of_week=getattr(transaction, "day_of_week"),
                            action=getattr(transaction, "action"),
                            timestamp=getattr(transaction, "timestamp"),
                            items=[TransactionItemResponse(item_name=item.item_name, item_quantity=item.item_quantity)
                                   for item in transaction.entries])
        for transaction in transactions]


def log_action(db: Session, action: str, items: list[ActionRequest]):
    transaction = Transaction(action=action)
    db.add(transaction)
    db.flush()

    for item in items:
        db.add(TransactionItem(transaction_id=transaction.id, item_name=item.name, item_quantity=item.quantity))


# Create a database connection
DATABASE_URL = 'sqlite:///inventory.db'
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()
