import sys

if __name__ == '__main__':
    if 'init_db' in sys.argv:
        from flaskr.database import init_db
        init_db()
