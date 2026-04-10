from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# ===================== 请注意这里的 URL =====================
# PostgreSQL 格式（后面我们登录数据库需要这个url来做身份验证）
DATABASE_URL = "postgresql+psycopg2://star_user:star_password@localhost:5432/star_db"
# ============================================================

# 创建数据库引擎
engine = create_engine(DATABASE_URL)

# 创建会话（用来操作数据库）
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 测试连接（运行这段代码不报错就是成功！）
def test_connection():
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        print("✅ Python 连接 Docker 数据库成功！")
        db.close()
    except Exception as e:
        print("❌ 连接失败：", e)

test_connection()