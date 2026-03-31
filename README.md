# PixelCast v1.0

Final package structure:

```
PixelCast_v1.0/
├── app/
├── frontend/
├── documentation/
│   └── index.html
├── .env.example
├── requirements.txt
├── README.md
└── install.sh
```

## Quick Start

1. Copy environment file:
   - `cp .env.example .env`
2. Review `.env` values (database password and secret key).
3. Run installer:
   - `chmod +x install.sh && ./install.sh`

## Notes

- Backend code is in `app/`.
- Frontend code is in `frontend/`.
- Documentation entry point is `documentation/index.html`.
