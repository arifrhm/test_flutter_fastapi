## test_flutter_fastapi

1. Create database flutter_db
2. Copy .env.sample
```
cp .env.sample .env

```

3. Migrate with alembic procedures
4. Start uvicorn server fastapi 
```
uvicorn main:app
```
5. To see endpoint documentation in browser :
```
http://localhost:8000/docs
```

6. Test endpoint with flutter or swagger
```
flutter pub get

flutter run
```
7. Select comfortable device to test

8. Happy coding :)
