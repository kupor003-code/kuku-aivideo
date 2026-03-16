"""数据库初始化脚本"""
from app.db.database import engine, Base
from app.models import (
    Project,
    CanvasNode,
    PromptVersion,
    VideoGeneration,
    ConversationMessage,
    StoryboardImage,
)


def init_db():
    """初始化数据库，创建所有表"""
    print("🚀 开始初始化数据库...")

    # 创建所有表
    Base.metadata.create_all(bind=engine)

    print("✅ 数据库表创建成功！")
    print("\n📊 已创建的表：")
    print("  - projects (项目表)")
    print("  - canvas_nodes (Canvas节点表)")
    print("  - prompt_versions (提示词版本表)")
    print("  - video_generations (视频生成记录表)")
    print("  - conversation_messages (对话消息表)")
    print("  - storyboard_images (分镜图片表)")
    print("\n✨ V2 数据库初始化完成！")


if __name__ == "__main__":
    init_db()
