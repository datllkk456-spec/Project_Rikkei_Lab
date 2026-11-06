
from fastapi import FastAPI, Depends,HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
import bcrypt
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer


from database import get_db
from models import User
from schemas import RegisterRequest
from schemas import RegisterRequest, LoginRequest
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

@app.get("/")
def home():
    return {"message": "Job Portal API đang hoạt động"}

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    statement = select(User)
    users = db.execute(statement).scalars().all()

    return users

@app.get("/users/{email}")
def get_user_by_email(email: str, db: Session = Depends(get_db)):
    statement = select(User).where(User.email == email)

    user = db.execute(statement).scalar_one_or_none()

    if user is None:
        return {"message": "Không tìm thấy người dùng"}

    return user

@app.post("/auth/register", status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):

    statement = select(User).where(User.email == data.email)
    existing_user = db.execute(statement).scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email đã được sử dụng"
        )

    hashed_password = bcrypt.hashpw(
        data.password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    new_user = User(
        full_name=data.full_name,
        email=data.email,
        password=hashed_password,
        role="candidate"
    )

    db.add(new_user)

    try:
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Email đã được sử dụng")

    return {
        "message": "Đăng ký thành công",
        "user_id": new_user.user_id,
        "full_name": new_user.full_name,
        "email": new_user.email,
        "role": new_user.role
    }

@app.post("/auth/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):

    statement = select(User).where(User.email == data.email)
    user = db.execute(statement).scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Email hoặc mật khẩu không chính xác"
        )

    if not bcrypt.checkpw(
        data.password.encode("utf-8"),
        user.password.encode("utf-8")
    ):
        raise HTTPException(
            status_code=401,
            detail="Email hoặc mật khẩu không chính xác"
        )

    if user.status != "active":
        raise HTTPException(
            status_code=403,
            detail="Tài khoản đã bị khóa hoặc vô hiệu hóa"
        )

    access_token = create_access_token({
        "sub": str(user.user_id),
        "role": user.role
    })

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.user_id,
        "full_name": user.full_name,
        "role": user.role
    }

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Token không hợp lệ hoặc đã hết hạn",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    statement = select(User).where(User.user_id == int(user_id))
    user = db.execute(statement).scalar_one_or_none()

    if user is None:
        raise credentials_exception

    if user.status != "active":
        raise HTTPException(
            status_code=403,
            detail="Tài khoản không hoạt động"
        )

    return user

@app.get("/auth/me")
def get_me(user: User = Depends(get_current_user)):
    return {
        "user_id": user.user_id,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role
    }


