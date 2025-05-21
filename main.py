from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm import joinedload
from dataBase import *
from datetime import datetime

app = FastAPI()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


#python -m  uvicorn main:app --reload --host 172.20.10.11

class UserLogin(BaseModel):
    login: str
    password: str


class RepairCreate(BaseModel):
    description_breakdown: str
    date_and_time_repair: str  # Формат: YYYY-MM-DD
    address_point_repair: str
    user_id: int

class UserResponse(BaseModel):
    id: int
    name: str
    surname: str
    patronymic: str
    phone: str
    date_of_birthday: str  # Или использовать datetime, если хотите
    address_residential: str
    bank_account_number: int
    role_id: int
    login: str
    password: str

class UserCreate(BaseModel):
    name: str
    surname: str
    patronymic: str
    phone: str
    date_of_birthday: str
    address_residential: str
    bank_account_number: int
    login: str
    password: str
    role_id: int = 1


class ReportCreate(BaseModel):
    point_departure: str
    type_point_departure: str
    sender: str
    point_destination: str
    type_point_destination: str
    recipient: str
    view_wood: str
    length_wood: int
    volume_wood: float
    report_date_time: str
    assortment_wood_type: str
    variety_wood_type: str
    user_id: int


class UserUpdate(BaseModel):
    name: str
    surname: str
    patronymic: str
    phone: str
    address_residential: str
    bank_account_number: int
    login: str
    password: str


class ReportResponse(BaseModel):
    id: int
    point_departure: str
    type_point_departure: str
    sender: str
    point_destination: str
    type_point_destination: str
    recipient: str
    view_wood: str
    length_wood: int
    volume_wood: float
    report_date_time: str
    assortment_wood_type: str
    variety_wood_type: str
    user_id: int


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/login")
async def login(user_login: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.login == user_login.login, User.password == user_login.password).first()

    if db_user is None:
        raise HTTPException(status_code=401, detail="Invalid login or password")

    return {
        "id": db_user.id,
        "name": db_user.name,
        "surname": db_user.surname,
        "patronymic": db_user.patronymic,
        "phone": db_user.phone,
        "date_of_birthday": db_user.date_of_birthday,
        "address_residential": db_user.address_residential,
        "bank_account_number": db_user.bank_account_number,
        "role_id": db_user.role_id,
        "password": db_user.password,
        "login": db_user.login
    }


@app.get("/getuser/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    # Получаем пользователя по user_id
    db_user = db.query(User).filter(User.id == user_id).first()

    # Если пользователь не найден, выбрасываем ошибку
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Возвращаем данные пользователя
    return {
        "id": db_user.id,  # Здесь вы ранее использовали db_user, что вызвало ошибку
        "name": db_user.name,
        "surname": db_user.surname,
        "patronymic": db_user.patronymic,
        "phone": db_user.phone,
        "date_of_birthday": db_user.date_of_birthday,
        "address_residential": db_user.address_residential,
        "bank_account_number": db_user.bank_account_number,
        "role_id": db_user.role_id,
        "password": db_user.password,
        "login": db_user.login
    }


@app.post("/repairs/")
async def create_repair(repair: RepairCreate, db: Session = Depends(get_db)):
    new_repair = Repair(
        description_breakdown=repair.description_breakdown,
        date_and_time_repair=repair.date_and_time_repair,
        address_point_repair=repair.address_point_repair,
        user_id=repair.user_id)
    try:
        db.add(new_repair)
        db.commit()
        db.refresh(new_repair)

    except Exception as e:
        raise HTTPException(status_code=400, detail="Internal server error")
    return new_repair


@app.post("/reports/")
async def create_report(report: ReportCreate, db: Session = Depends(get_db)):
    report_date_time = datetime.strptime(report.report_date_time, '%d/%m/%Y').date()

    new_report = Report(
        point_departure=report.point_departure,
        type_point_departure=report.type_point_departure,
        sender=report.sender,
        point_destination=report.point_destination,
        type_point_destination=report.type_point_destination,
        recipient=report.recipient,
        view_wood=report.view_wood,
        length_wood=report.length_wood,
        volume_wood=report.volume_wood,
        report_date_time=report_date_time,
        assortment_wood_type=report.assortment_wood_type,
        variety_wood_type=report.variety_wood_type,
        user_id=report.user_id
    )
    try:
        db.add(new_report)
        db.commit()
        db.refresh(new_report)

    except Exception as e:
        raise HTTPException(status_code=400, detail="Internal server error")
    return new_report


# @app.put("/users/{user_id}")
# async def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
#     db_user = db.query(User).filter(User.id == user_id).first()
#
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#
#     db_user.password = user_update.password
#     db_user.phone = user_update.phone
#     db_user.address_residential = user_update.address_residential
#     db_user.bank_account_number = user_update.bank_account_number
#
#     try:
#         db.commit()
#         db.refresh(db_user)
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=400, detail="Could not update user")
#
#     return db_user

@app.put("/users/{user_id}")
async def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    # Get the user from the database
    db_user = db.query(User).filter(User.id == user_id).first()

    # Raise an exception if the user is not found
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update fields
    db_user.name = user_update.name
    db_user.surname = user_update.surname
    db_user.patronymic = user_update.patronymic
    db_user.phone = user_update.phone
    db_user.address_residential = user_update.address_residential
    db_user.bank_account_number = user_update.bank_account_number
    db_user.login = user_update.login
    db_user.password = user_update.password

    try:
        db.commit()
        db.refresh(db_user)
        return {
            "id": db_user.id,
            "name": db_user.name,
            "surname": db_user.surname,
            "patronymic": db_user.patronymic,
            "phone": db_user.phone,
            "address_residential": db_user.address_residential,
            "bank_account_number": db_user.bank_account_number,
            "login": db_user.login,
            "password": db_user.password,
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update user")

@app.get("/user/{user_id}/car")
async def get_user_car(user_id: int, db: Session = Depends(get_db)):
    # Получаем автомобили пользователя
    user_cars = db.query(UserCar).filter(UserCar.user_id == user_id).all()

    if not user_cars:
        raise HTTPException(status_code=404, detail="Нет привязанных автомобилей для этого пользователя")

    car = user_cars[0]
    car_details = {
        "car_id": car.id,
        "state_number": car.car_park.state_number,
        "model": car.car_park.model,
        "stamp": car.car_park.stamp
    }

    return car_details


@app.get("/reports/user/{user_id}", response_model=list[ReportResponse])
async def get_reports_by_user(user_id: int, db: Session = Depends(get_db)):
    reports = db.query(Report).filter(Report.user_id == user_id).all()

    if not reports:
        raise HTTPException(status_code=404, detail="Нет отчетов для данного пользователя")

    return [{
        **report.__dict__,
        "report_date_time": report.report_date_time.isoformat()  # Преобразуем дату в строку
    } for report in reports]


@app.get("/reports/all", response_model=list[ReportResponse])
async def get_all_reports(db: Session = Depends(get_db)):
    reports = db.query(Report).all()
    if not reports:
        raise HTTPException(status_code=404, detail="В базе данных нет отчетов")
    return [{
        **report.__dict__,
        "report_date_time": report.report_date_time.isoformat()  # Преобразуем дату в строку
    } for report in reports]

@app.get("/users/role/1", response_model=list[UserResponse])
async def get_users_with_role_1(db: Session = Depends(get_db)):
    users = db.query(User).filter(User.role_id == 1).all()

    if not users:
        raise HTTPException(status_code=404, detail="Пользователи с role_id 1 не найдены")

    return [UserResponse(
        id=user.id,
        name=user.name,
        surname=user.surname,
        patronymic=user.patronymic,
        phone=user.phone,
        date_of_birthday=user.date_of_birthday.isoformat(),  # Преобразование в строку, если нужно
        address_residential=user.address_residential,
        bank_account_number=user.bank_account_number,
        role_id=user.role_id,
        login=user.login,
        password=user.password
    ) for user in users]


@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        date_of_birthday = datetime.strptime(user.date_of_birthday, '%Y-%m-%d').date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    # Create a new user object
    db_user = User(
        name=user.name,
        surname=user.surname,
        patronymic=user.patronymic,
        phone=user.phone,
        date_of_birthday=date_of_birthday,
        address_residential=user.address_residential,
        bank_account_number=user.bank_account_number,
        login=user.login,
        password=user.password,
        role_id=1  # Set role_id to 1
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        # Return the created user
        return UserResponse(
            id=db_user.id,
            name=db_user.name,
            surname=db_user.surname,
            patronymic=db_user.patronymic,
            phone=db_user.phone,
            date_of_birthday=db_user.date_of_birthday.isoformat(),
            address_residential=db_user.address_residential,
            bank_account_number=db_user.bank_account_number,
            role_id=db_user.role_id,
            login=db_user.login,
            password=db_user.password
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create user")