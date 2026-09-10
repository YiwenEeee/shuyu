import hashlib
import os
import re
import uuid
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional

import jwt
from dotenv import load_dotenv
from app.services.rag_service import rag
from app.services.embedding import EmbeddingError
from app.services.llm import LLMError
from fastapi import Depends, FastAPI, HTTPException, Query, Header, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, create_engine, func, or_
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./shuyu.db")
SECRET_KEY = os.getenv("SECRET_KEY", "shuyu-demo-secret-change-me-before-production-2026")
TOKEN_DAYS = int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS", "7"))
MATCH_SCORE_MIN = float(os.getenv("RAG_WEAK", "55"))
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase): pass


class User(Base):
    __tablename__ = "users"
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(128))
    nickname: Mapped[str] = mapped_column(String(80))
    avatar_path: Mapped[str] = mapped_column(String(500), default="/avatars/default.png")
    gender: Mapped[str] = mapped_column(String(20), default="unspecified")
    role: Mapped[str] = mapped_column(String(20), default="user")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class Book(Base):
    __tablename__ = "books"
    book_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    author: Mapped[str] = mapped_column(String(255), default="未知")
    isbn: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    cover_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    intro: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class Shelf(Base):
    __tablename__ = "shelves"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), index=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.book_id"))
    reading_status: Mapped[str] = mapped_column(String(20))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class Note(Base):
    __tablename__ = "notes"
    note_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), index=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.book_id"))
    content: Mapped[str] = mapped_column(Text)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    review_status: Mapped[str] = mapped_column(String(20), default="pending")
    review_reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    reviewed_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    topics: Mapped[str] = mapped_column(Text, default="[]")
    keywords: Mapped[str] = mapped_column(Text, default="[]")
    sentiment: Mapped[str] = mapped_column(String(10), default="neu")
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class Bottle(Base):
    __tablename__ = "bottles"
    bottle_id: Mapped[int] = mapped_column(primary_key=True)
    note_id: Mapped[int] = mapped_column(ForeignKey("notes.note_id"), unique=True)
    status: Mapped[str] = mapped_column(String(20), default="active")
    ai_status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at: Mapped[datetime] = mapped_column(DateTime)


class Interaction(Base):
    __tablename__ = "interactions"
    interaction_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    bottle_id: Mapped[int] = mapped_column(ForeignKey("bottles.bottle_id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class Friendship(Base):
    __tablename__ = "friendships"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    friend_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    bottle_id: Mapped[Optional[int]] = mapped_column(ForeignKey("bottles.bottle_id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class Like(Base):
    __tablename__ = "likes"
    id: Mapped[int] = mapped_column(primary_key=True)
    note_id: Mapped[int] = mapped_column(ForeignKey("notes.note_id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))


class Favorite(Base):
    __tablename__ = "favorites"
    id: Mapped[int] = mapped_column(primary_key=True)
    note_id: Mapped[int] = mapped_column(ForeignKey("notes.note_id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))


class Comment(Base):
    __tablename__ = "comments"
    comment_id: Mapped[int] = mapped_column(primary_key=True)
    note_id: Mapped[int] = mapped_column(ForeignKey("notes.note_id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


Base.metadata.create_all(engine)
app = FastAPI(title="书遇 API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
@app.middleware("http")
async def force_json_utf8(_: Request, call_next):
    """显式声明 UTF-8，兼容开发代理及非标准 JSON 解码器。"""
    response = await call_next(_)
    if response.headers.get("content-type", "").startswith("application/json"):
        response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response
UPLOAD_ROOT = Path("uploads")
UPLOAD_ROOT.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_ROOT)), name="uploads")


def ok(data=None, message="success"): return {"code": 200, "data": data, "message": message}
def fail(message, code=400): return JSONResponse(status_code=200, content={"code": code, "data": None, "message": message})
@app.exception_handler(HTTPException)
async def http_error(_, exc): return fail(str(exc.detail), exc.status_code if exc.status_code in (400, 401) else 400)
def now(): return datetime.utcnow()
def iso(value): return value.replace(tzinfo=timezone.utc).isoformat() if value else None
def hash_password(password): return hashlib.sha256(password.encode()).hexdigest()
def db_session():
    db = SessionLocal()
    try: yield db
    finally: db.close()
def token_for(user):
    expires = datetime.now(timezone.utc) + timedelta(days=TOKEN_DAYS)
    return jwt.encode({"sub": str(user.user_id), "exp": expires}, SECRET_KEY, algorithm="HS256"), expires
def current_user(authorization: Optional[str] = Header(default=None), db: Session = Depends(db_session)):
    if not authorization or not authorization.startswith("Bearer "): raise HTTPException(401, "请先登录")
    try: uid = int(jwt.decode(authorization[7:], SECRET_KEY, algorithms=["HS256"])["sub"])
    except jwt.PyJWTError: raise HTTPException(401, "登录已过期")
    user = db.get(User, uid)
    if not user: raise HTTPException(401, "用户不存在")
    return user
def admin(user=Depends(current_user)):
    if user.role != "admin": raise HTTPException(401, "需要管理员权限")
    return user
def user_data(u): return {"userId":u.user_id,"email":u.email,"nickname":u.nickname,"avatarPath":u.avatar_path,"gender":u.gender,"role":u.role}
def book_data(b): return {"bookId":b.book_id,"title":b.title,"author":b.author,"isbn":b.isbn,"coverPath":b.cover_path,"intro":b.intro,"status":b.status,"createdAt":iso(b.created_at),"updatedAt":iso(b.updated_at)}
def author_data(u): return {"userId":u.user_id,"nickname":u.nickname,"avatarPath":u.avatar_path}

class RegisterIn(BaseModel): email: EmailStr; password: str = Field(min_length=6); nickname: str = Field(min_length=1,max_length=80); avatarPath: str = "/avatars/default.png"; gender: Literal["male","female","unspecified"] = "unspecified"; role: Literal["user","admin"] = "user"
class LoginIn(BaseModel): email: EmailStr; password: str
class BookIn(BaseModel): title: str = Field(min_length=1); author: str = "未知"; isbn: Optional[str]=None; coverPath: Optional[str]=None; intro: Optional[str]=None; status: str="active"
class ShelfIn(BaseModel): bookId:int; readingStatus: Literal["wantToRead","reading","read"]
class NoteIn(BaseModel): bookId:int; content:str=Field(min_length=1); isPublic:bool=False; topics:list[str]=[]; keywords:list[str]=[]; sentiment:Literal["pos","neu","neg"]="neu"
class ReviewIn(BaseModel): reviewStatus:Literal["approved","rejected"]; reviewReason:Optional[str]=None
class CommentIn(BaseModel): content:str=Field(min_length=1,max_length=1000)
class FriendRequestIn(BaseModel): interactionId:int
class FriendRequestDecisionIn(BaseModel): status:Literal["accepted","rejected"]

def extract_ai_fields(content: str, topics: list[str], keywords: list[str], sentiment: str):
    """无外部模型时的可解释降级；C 的 AI 服务接入后替换本函数即可。"""
    text=content.strip()
    if not keywords:
        candidates=re.findall(r"[\u4e00-\u9fff]{2,8}|[A-Za-z]{3,}", text)
        keywords=list(dict.fromkeys(candidates))[:5]
    if not topics: topics=keywords[:3] or ["阅读感悟"]
    if sentiment=="neu":
        if re.search(r"喜欢|温暖|感动|美好|治愈|欣喜|快乐", text):sentiment="pos"
        elif re.search(r"难过|悲伤|失望|压抑|痛苦|愤怒", text):sentiment="neg"
    return topics, keywords, sentiment

def ai_note_fields(content: str, topics: list[str], keywords: list[str], sentiment: str):
    """优先使用 C 的 LLM 三栏；未配置真 key 时保证上传接口仍可用。"""
    if topics and keywords and sentiment != "neu": return topics, keywords, sentiment
    try:
        extracted = rag.analyze_note(content)
        return (topics or list(extracted.get("topics", [])), keywords or list(extracted.get("keywords", [])), extracted.get("sentiment", sentiment))
    except LLMError:
        return extract_ai_fields(content, topics, keywords, sentiment)

def publish_to_rag(note: Note, bottle: Bottle, db: Session):
    """将 C 的向量索引与 B 的 SQLite 漂流瓶主键和有效期保持一致。"""
    bottle.ai_status = "processing"
    db.flush()
    try:
        result = rag.publish_note(note.note_id, note.content, author_data(db.get(User, note.user_id)), book_data(db.get(Book, note.book_id)), True, "approved")
        if not result.get("published"):
            bottle.ai_status = "failed"
            return
        record = rag.store.get(note.note_id)
        if not record:
            bottle.ai_status = "failed"
            return
        record.update({"bottle_id": bottle.bottle_id, "status": bottle.status, "ai_status": "processing", "created_at": iso(bottle.created_at), "expires_at": iso(bottle.expires_at)})
        rag.store.upsert(note.note_id, record)
        bottle.ai_status = "ready" if rag.mark_ai_ready(note.note_id) else "failed"
    except EmbeddingError:
        bottle.ai_status = "failed"

@app.get("/api/health")
def health(): return ok({"status":"ok"})
@app.post("/api/uploads")
async def upload_image(file:UploadFile=File(...),purpose:Literal["avatar","cover"]=Form(...)):
    """头像/封面上传；前端使用返回的 data.filePath 原样提交。"""
    allowed={"image/jpeg":".jpg","image/png":".png","image/webp":".webp"}
    if file.content_type not in allowed:raise HTTPException(400,"仅支持 JPEG、PNG、WebP 图片")
    body=await file.read()
    if len(body)>5*1024*1024:raise HTTPException(400,"图片不能超过 5 MiB")
    folder=UPLOAD_ROOT/("avatars" if purpose=="avatar" else "covers");folder.mkdir(exist_ok=True)
    name=f"{uuid.uuid4().hex}{allowed[file.content_type]}";(folder/name).write_bytes(body)
    return ok({"filePath":f"/uploads/{folder.name}/{name}"})
@app.post("/api/auth/register")
def register(payload:RegisterIn, db:Session=Depends(db_session)):
    if db.scalar(db.query(User).filter(User.email == payload.email).statement): raise HTTPException(400,"邮箱已注册")
    u=User(email=payload.email,password_hash=hash_password(payload.password),nickname=payload.nickname,avatar_path=payload.avatarPath,gender=payload.gender,role=payload.role); db.add(u); db.commit(); db.refresh(u)
    token, expires=token_for(u); return ok({**user_data(u),"token":token,"expiresAt":iso(expires)},"注册成功")
@app.post("/api/auth/login")
def login(payload:LoginIn, db:Session=Depends(db_session)):
    u=db.query(User).filter(User.email==payload.email).first()
    if not u or u.password_hash != hash_password(payload.password): raise HTTPException(401,"邮箱或密码错误")
    token,expires=token_for(u); return ok({"token":token,"expiresAt":iso(expires)})
@app.get("/api/me")
def me(user=Depends(current_user)): return ok(user_data(user))

@app.get("/api/books")
def books(keyword:str="",pageNum:int=Query(1,ge=1),pageSize:int=Query(10,ge=1,le=100), db:Session=Depends(db_session)):
    q=db.query(Book).filter(Book.status=="active")
    if keyword: q=q.filter(or_(Book.title.contains(keyword),Book.author.contains(keyword)))
    total=q.count();items=q.order_by(Book.book_id.desc()).offset((pageNum-1)*pageSize).limit(pageSize).all()
    return ok({"list":[book_data(x) for x in items],"total":total,"pageNum":pageNum,"pageSize":pageSize})
@app.get("/api/books/{book_id}")
def get_book(book_id:int,db:Session=Depends(db_session)):
    book=db.get(Book,book_id)
    if not book:raise HTTPException(400,"书籍不存在")
    return ok(book_data(book))
@app.get("/api/admin/books")
def admin_books(keyword:str="",status:Optional[Literal["active","inactive"]]=None,needsCompletion:Optional[bool]=None,pageNum:int=Query(1,ge=1),pageSize:int=Query(10,ge=1,le=100),db:Session=Depends(db_session),_=Depends(admin)):
    """管理员书籍分页列表：包含已下架书籍。"""
    q=db.query(Book)
    if keyword:q=q.filter(or_(Book.title.contains(keyword),Book.author.contains(keyword)))
    if status:q=q.filter(Book.status==status)
    if needsCompletion is True:q=q.filter(or_(Book.cover_path.is_(None),Book.intro.is_(None)))
    if needsCompletion is False:q=q.filter(Book.cover_path.is_not(None),Book.intro.is_not(None))
    total=q.count();items=q.order_by(Book.book_id.desc()).offset((pageNum-1)*pageSize).limit(pageSize).all()
    return ok({"list":[book_data(x) for x in items],"total":total,"pageNum":pageNum,"pageSize":pageSize})
@app.post("/api/admin/books")
def create_book(payload:BookIn, db:Session=Depends(db_session), _=Depends(admin)):
    b=Book(title=payload.title,author=payload.author,isbn=payload.isbn,cover_path=payload.coverPath,intro=payload.intro,status=payload.status); db.add(b);db.commit();db.refresh(b);return ok(book_data(b))
@app.put("/api/admin/books/{book_id}")
def update_book(book_id:int,payload:BookIn,db:Session=Depends(db_session),_=Depends(admin)):
    b=db.get(Book,book_id)
    if not b: raise HTTPException(400,"书籍不存在")
    for field,value in {"title":payload.title,"author":payload.author,"isbn":payload.isbn,"cover_path":payload.coverPath,"intro":payload.intro,"status":payload.status}.items(): setattr(b,field,value)
    db.commit(); return ok(book_data(b))
@app.delete("/api/admin/books/{book_id}")
def remove_book(book_id:int,db:Session=Depends(db_session),_=Depends(admin)):
    b=db.get(Book,book_id)
    if not b: raise HTTPException(400,"书籍不存在")
    b.status="inactive";db.commit();return ok(None,"已下架")

@app.get("/api/me/books")
def my_books(readingStatus:Optional[str]=None,pageNum:int=Query(1,ge=1),pageSize:int=Query(10,ge=1,le=100),user=Depends(current_user),db:Session=Depends(db_session)):
    q=db.query(Shelf).filter(Shelf.user_id==user.user_id)
    if readingStatus: q=q.filter(Shelf.reading_status==readingStatus)
    total=q.count();items=q.order_by(Shelf.updated_at.desc(),Shelf.book_id.desc()).offset((pageNum-1)*pageSize).limit(pageSize).all()
    return ok({"list":[{"readingStatus":x.reading_status,"book":book_data(db.get(Book,x.book_id)),"updatedAt":iso(x.updated_at)} for x in items],"total":total,"pageNum":pageNum,"pageSize":pageSize})
@app.put("/api/me/books")
def set_book(payload:ShelfIn,user=Depends(current_user),db:Session=Depends(db_session)):
    if not db.get(Book,payload.bookId): raise HTTPException(400,"书籍不存在")
    x=db.query(Shelf).filter_by(user_id=user.user_id,book_id=payload.bookId).first()
    if x: x.reading_status=payload.readingStatus
    else: x=Shelf(user_id=user.user_id,book_id=payload.bookId,reading_status=payload.readingStatus);db.add(x)
    db.commit();return ok({"readingStatus":x.reading_status,"book":book_data(db.get(Book,x.book_id)),"updatedAt":iso(x.updated_at)})
@app.delete("/api/me/books/{book_id}")
def remove_my_book(book_id:int,user=Depends(current_user),db:Session=Depends(db_session)):
    item=db.query(Shelf).filter_by(user_id=user.user_id,book_id=book_id).first()
    if item:db.delete(item);db.commit()
    return ok(None,"已移出书单")
@app.get("/api/me/current-reading")
def current_reading(user=Depends(current_user),db:Session=Depends(db_session)):
    x=db.query(Shelf).filter_by(user_id=user.user_id,reading_status="reading").order_by(Shelf.updated_at.desc()).first()
    return ok(None if not x else {"book":book_data(db.get(Book,x.book_id)),"updatedAt":iso(x.updated_at)})

def note_data(n, viewer, db, include_content=True):
    import json
    likes=db.query(Like).filter_by(note_id=n.note_id); favs=db.query(Favorite).filter_by(note_id=n.note_id); comments=db.query(Comment).filter_by(note_id=n.note_id).order_by(Comment.comment_id.desc()).all()
    result={"noteId":n.note_id,"author":author_data(db.get(User,n.user_id)),"book":book_data(db.get(Book,n.book_id)),"bookId":n.book_id,"isPublic":n.is_public,"reviewStatus":n.review_status,"reviewReason":n.review_reason,"reviewedBy":n.reviewed_by,"topics":json.loads(n.topics),"keywords":json.loads(n.keywords),"sentiment":n.sentiment,"createdAt":iso(n.created_at),"updatedAt":iso(n.updated_at),"deletedAt":iso(n.deleted_at),"likeCount":likes.count(),"favoriteCount":favs.count(),"commentCount":len(comments),"isLiked":bool(viewer and likes.filter_by(user_id=viewer.user_id).first()),"isFavorited":bool(viewer and favs.filter_by(user_id=viewer.user_id).first())}
    if include_content: result["content"]=n.content
    return result
@app.post("/api/notes")
def create_note(payload:NoteIn,user=Depends(current_user),db:Session=Depends(db_session)):
    import json
    if not db.get(Book,payload.bookId): raise HTTPException(400,"书籍不存在")
    topics,keywords,sentiment=ai_note_fields(payload.content,payload.topics,payload.keywords,payload.sentiment)
    n=Note(user_id=user.user_id,book_id=payload.bookId,content=payload.content,is_public=payload.isPublic,topics=json.dumps(topics),keywords=json.dumps(keywords),sentiment=sentiment);db.add(n);db.commit();db.refresh(n);return ok(note_data(n,user,db),"笔记已提交审核")
@app.get("/api/me/notes")
def my_notes(isPublic:Optional[bool]=None,reviewStatus:Optional[str]=None,bookId:Optional[int]=None,pageNum:int=Query(1,ge=1),pageSize:int=Query(10,ge=1,le=100),user=Depends(current_user),db:Session=Depends(db_session)):
    q=db.query(Note).filter(Note.user_id==user.user_id,Note.deleted_at.is_(None))
    if isPublic is not None:q=q.filter(Note.is_public==isPublic)
    if reviewStatus:q=q.filter(Note.review_status==reviewStatus)
    if bookId:q=q.filter(Note.book_id==bookId)
    total=q.count();items=q.order_by(Note.created_at.desc(),Note.note_id.desc()).offset((pageNum-1)*pageSize).limit(pageSize).all()
    return ok({"list":[note_data(n,user,db) for n in items],"total":total,"pageNum":pageNum,"pageSize":pageSize})
@app.delete("/api/notes/{note_id}")
def delete_note(note_id:int,user=Depends(current_user),db:Session=Depends(db_session)):
    n=db.get(Note,note_id)
    if not n or n.user_id!=user.user_id:raise HTTPException(400,"笔记不存在")
    n.deleted_at=now();rag.remove_note(note_id);db.commit();return ok(None,"已删除")
@app.get("/api/admin/notes")
def pending_notes(reviewStatus:Optional[str]=None,authorId:Optional[int]=None,bookId:Optional[int]=None,isPublic:Optional[bool]=None,includeDeleted:bool=False,pageNum:int=Query(1,ge=1),pageSize:int=Query(10,ge=1,le=100),db:Session=Depends(db_session),_=Depends(admin)):
    q=db.query(Note)
    if reviewStatus:q=q.filter(Note.review_status==reviewStatus)
    if authorId:q=q.filter(Note.user_id==authorId)
    if bookId:q=q.filter(Note.book_id==bookId)
    if isPublic is not None:q=q.filter(Note.is_public==isPublic)
    if not includeDeleted:q=q.filter(Note.deleted_at.is_(None))
    total=q.count();items=q.order_by(Note.created_at.desc(),Note.note_id.desc()).offset((pageNum-1)*pageSize).limit(pageSize).all()
    return ok({"list":[note_data(n,None,db) for n in items],"total":total,"pageNum":pageNum,"pageSize":pageSize})
@app.put("/api/admin/notes/{note_id}/review")
def review(note_id:int,payload:ReviewIn,db:Session=Depends(db_session),user=Depends(admin)):
    n=db.get(Note,note_id)
    if not n or n.deleted_at:raise HTTPException(400,"笔记不存在")
    if payload.reviewStatus=="rejected" and not payload.reviewReason:raise HTTPException(400,"拒绝时必须填写原因")
    n.review_status=payload.reviewStatus;n.review_reason=payload.reviewReason if payload.reviewStatus=="rejected" else None;n.reviewed_by=user.user_id
    if payload.reviewStatus=="rejected":rag.remove_note(n.note_id)
    if payload.reviewStatus=="approved" and n.is_public and not db.query(Bottle).filter_by(note_id=n.note_id).first():
        bottle=Bottle(note_id=n.note_id,ai_status="pending",expires_at=now()+timedelta(days=7));db.add(bottle);db.flush();publish_to_rag(n,bottle,db)
    db.commit();return ok(note_data(n,user,db))

def match_score(source: Note, candidate: Note) -> float:
    """Deterministic fallback; C's vector service can replace this with cosine similarity."""
    words=lambda text:set(re.findall(r"[\w\u4e00-\u9fff]+",text.lower()))
    a,b=words(source.content),words(candidate.content)
    return round(100*len(a&b)/len(a|b),1) if a and b else 0.0
def bottle_data(b,source,db):
    n=db.get(Note,b.note_id)
    return {"bottleId":b.bottle_id,"author":author_data(db.get(User,n.user_id)),"book":book_data(db.get(Book,n.book_id)),"status":b.status,"aiStatus":b.ai_status,"createdAt":iso(b.created_at),"expiresAt":iso(b.expires_at),"contentPreview":n.content[:100],"noteId":n.note_id,"recommendation":None,"matchScore":match_score(source,n)}
@app.get("/api/bottles/matches")
def matches(noteId:int,pageNum:int=Query(1,ge=1),pageSize:int=Query(10,ge=1,le=100),user=Depends(current_user),db:Session=Depends(db_session)):
    source=db.get(Note,noteId)
    if not source or source.user_id!=user.user_id or not source.is_public or source.review_status!="approved" or source.deleted_at:raise HTTPException(400,"只能用本人已审核的公开笔记进行匹配")
    my_note_ids={x.note_id for x in db.query(Note).filter_by(user_id=user.user_id).all()}
    acquired_bottles={x.bottle_id for x in db.query(Interaction).filter_by(user_id=user.user_id).all()}
    excluded_note_ids={db.get(Bottle,bid).note_id for bid in acquired_bottles if db.get(Bottle,bid)}
    try:
        rag_items=rag.match(source.note_id,source.content,my_note_ids,excluded_note_ids)
    except EmbeddingError as exc:
        raise HTTPException(400,f"AI 匹配暂不可用: {exc}")
    items=[]
    for item in rag_items:
        bottle=db.get(Bottle,item["bottleId"]);candidate=db.get(Note,item["noteId"])
        if bottle and candidate and bottle.note_id==candidate.note_id and bottle.status=="active" and bottle.ai_status=="ready" and bottle.expires_at>now() and candidate.is_public and candidate.review_status=="approved" and not candidate.deleted_at and candidate.user_id!=user.user_id and bottle.bottle_id not in acquired_bottles:items.append(item)
    total=len(items);start=(pageNum-1)*pageSize
    return ok({"list":items[start:start+pageSize],"total":total,"pageNum":pageNum,"pageSize":pageSize})
@app.post("/api/bottles/{bottle_id}/open")
def open_bottle(bottle_id:int,user=Depends(current_user),db:Session=Depends(db_session)):
    b=db.get(Bottle,bottle_id)
    if not b or b.status!="active" or b.expires_at<=now():raise HTTPException(400,"漂流瓶不可用")
    if db.get(Note,b.note_id).user_id==user.user_id:raise HTTPException(400,"不能打开自己的漂流瓶")
    x=db.query(Interaction).filter_by(user_id=user.user_id,bottle_id=bottle_id).first()
    if not x:x=Interaction(user_id=user.user_id,bottle_id=bottle_id);db.add(x);db.commit();db.refresh(x)
    return ok({"interactionId":x.interaction_id,"noteId":b.note_id})
@app.post("/api/bottles/{bottle_id}/acquire")
def acquire_bottle(bottle_id:int,user=Depends(current_user),db:Session=Depends(db_session)):
    """正式联调接口；data.myInteraction.interactionId 用于后续发起书友申请。"""
    b=db.get(Bottle,bottle_id)
    if not b or b.status!="active" or b.ai_status!="ready" or b.expires_at<=now():raise HTTPException(400,"漂流瓶不可获取")
    n=db.get(Note,b.note_id)
    if n.user_id==user.user_id or not n.is_public or n.review_status!="approved" or n.deleted_at:raise HTTPException(400,"漂流瓶不可获取")
    x=db.query(Interaction).filter_by(user_id=user.user_id,bottle_id=bottle_id).first()
    if not x:x=Interaction(user_id=user.user_id,bottle_id=bottle_id);db.add(x);db.commit();db.refresh(x)
    import json
    return ok({"bottleId":b.bottle_id,"author":author_data(db.get(User,n.user_id)),"book":book_data(db.get(Book,n.book_id)),"status":b.status,"aiStatus":b.ai_status,"createdAt":iso(b.created_at),"expiresAt":iso(b.expires_at),"content":n.content,"topics":json.loads(n.topics),"keywords":json.loads(n.keywords),"emotion":n.sentiment,"aiMessage":None,"myInteraction":{"interactionId":x.interaction_id,"bottleId":b.bottle_id,"receiver":author_data(user),"acquiredAt":iso(x.created_at),"stickyText":None,"stickyAt":None,"replyText":None,"repliedAt":None},"noteId":n.note_id})
@app.post("/api/interactions/{interaction_id}/friend-requests")
def friend_request(interaction_id:int,user=Depends(current_user),db:Session=Depends(db_session)):
    x=db.get(Interaction,interaction_id)
    if not x or x.user_id!=user.user_id:raise HTTPException(400,"互动记录不存在")
    target=db.get(Note,db.get(Bottle,x.bottle_id).note_id).user_id;f=db.query(Friendship).filter_by(user_id=user.user_id,friend_id=target).first()
    if not f:f=Friendship(user_id=user.user_id,friend_id=target,bottle_id=x.bottle_id);db.add(f);db.commit();db.refresh(f)
    return ok({"id":f.id,"userId":f.user_id,"friendId":f.friend_id,"status":f.status,"createdAt":iso(f.created_at)})
@app.post("/api/friend-requests")
def create_friend_request(payload:FriendRequestIn,user=Depends(current_user),db:Session=Depends(db_session)):
    """正式协议兼容：前端在 body 传 acquire 返回的 interactionId。"""
    x=db.get(Interaction,payload.interactionId)
    if not x or x.user_id!=user.user_id:raise HTTPException(400,"互动记录不存在")
    target=db.get(Note,db.get(Bottle,x.bottle_id).note_id).user_id
    f=db.query(Friendship).filter_by(user_id=user.user_id,friend_id=target).first()
    if not f:f=Friendship(user_id=user.user_id,friend_id=target,bottle_id=x.bottle_id);db.add(f);db.commit();db.refresh(f)
    return ok({"requestId":f.id,"requester":author_data(db.get(User,f.user_id)),"receiver":author_data(db.get(User,f.friend_id)),"bottleId":f.bottle_id,"status":f.status,"createdAt":iso(f.created_at),"handledAt":None})
@app.get("/api/friend-requests")
def requests(user=Depends(current_user),db:Session=Depends(db_session)):
    return ok([{"id":x.id,"userId":x.user_id,"friendId":x.friend_id,"status":x.status,"createdAt":iso(x.created_at),"user":author_data(db.get(User,x.user_id))} for x in db.query(Friendship).filter_by(friend_id=user.user_id,status="pending").all()])
@app.get("/api/me/friend-requests")
def my_friend_requests(direction:Literal["sent","received"],status:Optional[str]=None,pageNum:int=Query(1,ge=1),pageSize:int=Query(10,ge=1,le=100),user=Depends(current_user),db:Session=Depends(db_session)):
    q=db.query(Friendship).filter(Friendship.user_id==user.user_id if direction=="sent" else Friendship.friend_id==user.user_id)
    if status:q=q.filter(Friendship.status==status)
    total=q.count();items=q.order_by(Friendship.created_at.desc(),Friendship.id.desc()).offset((pageNum-1)*pageSize).limit(pageSize).all()
    return ok({"list":[{"requestId":f.id,"requester":author_data(db.get(User,f.user_id)),"receiver":author_data(db.get(User,f.friend_id)),"bottleId":f.bottle_id,"status":f.status,"createdAt":iso(f.created_at),"handledAt":None} for f in items],"total":total,"pageNum":pageNum,"pageSize":pageSize})
@app.put("/api/friend-requests/{request_id}")
def answer_request(request_id:int,answer:Literal["accepted","rejected"],user=Depends(current_user),db:Session=Depends(db_session)):
    f=db.get(Friendship,request_id)
    if not f or f.friend_id!=user.user_id or f.status!="pending":raise HTTPException(400,"申请不存在")
    f.status=answer;db.commit();return ok({"id":f.id,"status":f.status})
@app.patch("/api/friend-requests/{request_id}")
def handle_friend_request(request_id:int,payload:FriendRequestDecisionIn,user=Depends(current_user),db:Session=Depends(db_session)):
    """正式协议：接收者以 JSON body 的 status 接受或拒绝申请。"""
    f=db.get(Friendship,request_id)
    if not f or f.friend_id!=user.user_id:raise HTTPException(400,"申请不存在")
    if f.status=="pending":f.status=payload.status;db.commit()
    elif f.status!=payload.status:raise HTTPException(400,"申请已处理")
    return ok({"requestId":f.id,"requester":author_data(db.get(User,f.user_id)),"receiver":author_data(db.get(User,f.friend_id)),"bottleId":f.bottle_id,"status":f.status,"createdAt":iso(f.created_at),"handledAt":iso(f.created_at) if f.status!="pending" else None})

def friend_ids(user_id,db):
    rows=db.query(Friendship).filter(Friendship.status=="accepted",or_(Friendship.user_id==user_id,Friendship.friend_id==user_id)).all()
    return {x.friend_id if x.user_id==user_id else x.user_id for x in rows}
@app.get("/api/me/friends")
def my_friends(pageNum:int=Query(1,ge=1),pageSize:int=Query(10,ge=1,le=100),user=Depends(current_user),db:Session=Depends(db_session)):
    rows=db.query(Friendship).filter(Friendship.status=="accepted",or_(Friendship.user_id==user.user_id,Friendship.friend_id==user.user_id)).order_by(Friendship.created_at.desc(),Friendship.id.desc()).all()
    total=len(rows);items=rows[(pageNum-1)*pageSize:pageNum*pageSize]
    return ok({"list":[{"user":author_data(db.get(User,f.friend_id if f.user_id==user.user_id else f.user_id)),"becameFriendsAt":iso(f.created_at)} for f in items],"total":total,"pageNum":pageNum,"pageSize":pageSize})
@app.delete("/api/me/friends/{user_id}")
def remove_friend(user_id:int,user=Depends(current_user),db:Session=Depends(db_session)):
    rows=db.query(Friendship).filter(Friendship.status=="accepted",or_((Friendship.user_id==user.user_id)&(Friendship.friend_id==user_id),(Friendship.user_id==user_id)&(Friendship.friend_id==user.user_id))).all()
    for row in rows:db.delete(row)
    db.commit();return ok(None,"已解除书友关系")
def wall_note(n,user,db):
    data=note_data(n,user,db);data["comments"]=[]
    for c in db.query(Comment).filter_by(note_id=n.note_id).order_by(Comment.comment_id.desc()).all():data["comments"].append({"commentId":c.comment_id,"noteId":c.note_id,"author":author_data(db.get(User,c.user_id)),"content":c.content,"createdAt":iso(c.created_at),"canDelete":c.user_id==user.user_id})
    return data
@app.get("/api/wall")
@app.get("/api/wall/notes")
def wall(pageNum:int=Query(1,ge=1),pageSize:int=Query(10,ge=1,le=100),user=Depends(current_user),db:Session=Depends(db_session)):
    ids=friend_ids(user.user_id,db)
    q=db.query(Note).filter(Note.user_id.in_(ids),Note.user_id!=user.user_id,Note.is_public==True,Note.review_status=="approved",Note.deleted_at.is_(None)).order_by(Note.created_at.desc(),Note.note_id.desc()) if ids else db.query(Note).filter(False)
    total=q.count();rows=q.offset((pageNum-1)*pageSize).limit(pageSize).all()
    return ok({"list":[wall_note(n,user,db) for n in rows],"total":total,"pageNum":pageNum,"pageSize":pageSize})
@app.get("/api/me/favorites")
def my_favorites(pageNum:int=Query(1,ge=1),pageSize:int=Query(10,ge=1,le=100),user=Depends(current_user),db:Session=Depends(db_session)):
    q=db.query(Note).join(Favorite,Favorite.note_id==Note.note_id).filter(Favorite.user_id==user.user_id,Note.is_public==True,Note.review_status=="approved",Note.deleted_at.is_(None)).order_by(Favorite.id.desc(),Note.note_id.desc())
    total=q.count();items=q.offset((pageNum-1)*pageSize).limit(pageSize).all()
    return ok({"list":[note_data(n,user,db) for n in items],"total":total,"pageNum":pageNum,"pageSize":pageSize})
def toggle(model,note_id,user,db):
    if not db.get(Note,note_id):raise HTTPException(400,"笔记不存在")
    x=db.query(model).filter_by(note_id=note_id,user_id=user.user_id).first()
    if x:db.delete(x);active=False
    else:db.add(model(note_id=note_id,user_id=user.user_id));active=True
    db.commit();return ok({"active":active})
def social_data(note_id,user,db):
    return {"noteId":note_id,"likeCount":db.query(Like).filter_by(note_id=note_id).count(),"favoriteCount":db.query(Favorite).filter_by(note_id=note_id).count(),"commentCount":db.query(Comment).filter_by(note_id=note_id).count(),"isLiked":bool(db.query(Like).filter_by(note_id=note_id,user_id=user.user_id).first()),"isFavorited":bool(db.query(Favorite).filter_by(note_id=note_id,user_id=user.user_id).first())}
def set_social(model,note_id,user,db,enabled):
    if not db.get(Note,note_id):raise HTTPException(400,"笔记不存在")
    x=db.query(model).filter_by(note_id=note_id,user_id=user.user_id).first()
    if enabled and not x:db.add(model(note_id=note_id,user_id=user.user_id))
    if not enabled and x:db.delete(x)
    db.commit();return ok(social_data(note_id,user,db))
@app.put("/api/notes/{note_id}/like")
def put_like(note_id:int,user=Depends(current_user),db:Session=Depends(db_session)):return set_social(Like,note_id,user,db,True)
@app.delete("/api/notes/{note_id}/like")
def delete_like(note_id:int,user=Depends(current_user),db:Session=Depends(db_session)):return set_social(Like,note_id,user,db,False)
@app.put("/api/notes/{note_id}/favorite")
def put_favorite(note_id:int,user=Depends(current_user),db:Session=Depends(db_session)):return set_social(Favorite,note_id,user,db,True)
@app.delete("/api/notes/{note_id}/favorite")
def delete_favorite(note_id:int,user=Depends(current_user),db:Session=Depends(db_session)):return set_social(Favorite,note_id,user,db,False)
@app.post("/api/notes/{note_id}/like")
def like(note_id:int,user=Depends(current_user),db:Session=Depends(db_session)):return toggle(Like,note_id,user,db)
@app.post("/api/notes/{note_id}/favorite")
def favorite(note_id:int,user=Depends(current_user),db:Session=Depends(db_session)):return toggle(Favorite,note_id,user,db)
@app.post("/api/notes/{note_id}/comments")
def add_comment(note_id:int,payload:CommentIn,user=Depends(current_user),db:Session=Depends(db_session)):
    if not db.get(Note,note_id):raise HTTPException(400,"笔记不存在")
    c=Comment(note_id=note_id,user_id=user.user_id,content=payload.content);db.add(c);db.commit();db.refresh(c);return ok({"commentId":c.comment_id,"noteId":note_id,"author":author_data(user),"content":c.content,"createdAt":iso(c.created_at),"canDelete":True})
@app.get("/api/notes/{note_id}/comments")
def list_comments(note_id:int,pageNum:int=Query(1,ge=1),pageSize:int=Query(10,ge=1,le=100),user=Depends(current_user),db:Session=Depends(db_session)):
    note=db.get(Note,note_id)
    if not note:raise HTTPException(400,"笔记不存在")
    visible=note.is_public and note.review_status=="approved" and not note.deleted_at
    if not visible and note.user_id!=user.user_id and user.role!="admin":raise HTTPException(400,"无权查看评论")
    q=db.query(Comment).filter_by(note_id=note_id).order_by(Comment.created_at.desc(),Comment.comment_id.desc())
    total=q.count();items=q.offset((pageNum-1)*pageSize).limit(pageSize).all()
    return ok({"list":[{"commentId":c.comment_id,"noteId":c.note_id,"author":author_data(db.get(User,c.user_id)),"content":c.content,"createdAt":iso(c.created_at),"canDelete":c.user_id==user.user_id or note.user_id==user.user_id or user.role=="admin"} for c in items],"total":total,"pageNum":pageNum,"pageSize":pageSize})
@app.delete("/api/comments/{comment_id}")
def remove_comment(comment_id:int,user=Depends(current_user),db:Session=Depends(db_session)):
    c=db.get(Comment,comment_id)
    if not c or c.user_id!=user.user_id:raise HTTPException(400,"评论不存在")
    db.delete(c);db.commit();return ok(None,"已删除")
@app.put("/api/bottles/{bottle_id}/ai-status")
def set_ai_status(bottle_id:int,aiStatus:Literal["pending","processing","ready","failed"],db:Session=Depends(db_session),_=Depends(admin)):
    """C 同学的 RAG 服务完成 embedding 后调用；ready 的瓶子才返回给匹配接口。"""
    b=db.get(Bottle,bottle_id)
    if not b:raise HTTPException(400,"漂流瓶不存在")
    b.ai_status=aiStatus;db.commit();return ok({"bottleId":b.bottle_id,"aiStatus":b.ai_status})
@app.get("/api/admin/bottles")
def pending_bottles(aiStatus:Optional[str]=None,db:Session=Depends(db_session),_=Depends(admin)):
    q=db.query(Bottle)
    if aiStatus:q=q.filter(Bottle.ai_status==aiStatus)
    return ok([{"bottleId":b.bottle_id,"noteId":b.note_id,"aiStatus":b.ai_status,"status":b.status,"createdAt":iso(b.created_at),"expiresAt":iso(b.expires_at)} for b in q.order_by(Bottle.bottle_id.desc()).all()])
