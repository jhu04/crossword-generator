from firebase_admin import credentials, db, initialize_app

cred = credentials.Certificate('./data/firebase-key.json')
initialize_app(cred, {
    'databaseURL': "https://console.firebase.google.com/project/crossword-29fcf/database/crossword-29fcf-default-rtdb/data/~2F"
})

ref = db.reference('/')
print(ref.get())