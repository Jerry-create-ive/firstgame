#!/usr/bin/env python3
import os
import sys

def check_python():
    print("✓ Python 版本:", sys.version)

def check_django():
    try:
        import django
        print("✓ Django 版本:", django.VERSION)
        return True
    except ImportError:
        print("✗ Django 未安装")
        return False

def check_files():
    print("\n=== 检查文件结构 ===")
    
    files = [
        ('manage.py', '项目管理文件'),
        ('red_story/settings.py', '配置文件'),
        ('red_story/urls.py', 'URL路由'),
        ('main/views.py', '视图函数'),
        ('main/templates/index.html', '主模板'),
        ('main/templates/test_images.html', '测试模板'),
    ]
    
    all_exists = True
    for path, desc in files:
        full_path = os.path.join(os.getcwd(), path)
        if os.path.exists(full_path):
            print(f"✓ {path} - {desc}")
        else:
            print(f"✗ {path} - 缺失")
            all_exists = False
    
    return all_exists

def check_images():
    print("\n=== 检查图片资源 ===")
    image_dir = os.path.join(os.getcwd(), 'main/static/image')
    if os.path.exists(image_dir):
        images = [f for f in os.listdir(image_dir) if f.endswith('.jpg')]
        print(f"✓ 图片目录存在，共 {len(images)} 张图片")
        for img in sorted(images):
            size = os.path.getsize(os.path.join(image_dir, img))
            print(f"  - {img} ({size} bytes)")
        return True
    else:
        print("✗ 图片目录不存在")
        return False

def check_settings():
    print("\n=== 检查配置 ===")
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'red_story.settings')
        import django
        django.setup()
        
        from django.conf import settings
        print(f"✓ DEBUG 模式: {settings.DEBUG}")
        print(f"✓ STATIC_URL: {settings.STATIC_URL}")
        print(f"✓ STATICFILES_DIRS: {settings.STATICFILES_DIRS}")
        print(f"✓ 已安装应用: {settings.INSTALLED_APPS}")
        
        return True
    except Exception as e:
        print(f"✗ 配置检查失败: {e}")
        return False

def main():
    print("=" * 50)
    print("     Django 项目诊断工具")
    print("=" * 50)
    
    check_python()
    
    if not check_django():
        print("\n建议执行: pip install django")
        return
    
    check_files()
    check_images()
    
    if check_settings():
        print("\n" + "=" * 50)
        print("✓ 项目配置正常")
        print("=" * 50)
        print("\n启动命令:")
        print("  python manage.py runserver 8000")
        print("\n访问地址:")
        print("  主游戏: http://localhost:8000/")
        print("  图片测试: http://localhost:8000/test/")

if __name__ == '__main__':
    main()