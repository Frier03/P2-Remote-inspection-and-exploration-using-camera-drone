from fastapi.middleware.cors import CORSMiddleware

def add_origins(app: object):
    origins = [ # Which request the API will allow
        "http://localhost",
        "http://localhost:3000",
        "http://192.168.1.142:3000",
        "http://172.26.50.10:3000"
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    return app