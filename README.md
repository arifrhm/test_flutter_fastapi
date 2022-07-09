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
6. Extract shamo-flutter.zip

7. Test endpoint with flutter by running flutter app
```
flutter create .

flutter pub get

flutter run
```
8. Select comfortable device to test

9. Happy coding :)
