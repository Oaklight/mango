# mango-website

this branch hosts project page related files

## Setup

Build with MkDocs

```bash
pip install mkdocs
pip install mkdocs-material
```

## Deploy

deploy to github pages

```bash
mkdocs gh-deploy
```

## Structure

```bash
./mango-website/
├── docs
│   ├── assets
│   │   └── images
│   │       ├── mango.png
│   │       └── ...
│   ├── contact.md
│   ├── data.md
│   └── index.md
├── mkdocs.yml
└── README.md
```

- `assets`

    images are stored in `docs/assets/images` folder <br>
    any other assets should be stored in `docs/assets` folder

- `docs` markdown templates

    `docs/index.md` is the home page <br>
    `docs/data.md` is the data detail page <br>
    `docs/contact.md` is the contact page <br>
    any other pages should be added to `docs` folder and linked in `mkdocs.yml`