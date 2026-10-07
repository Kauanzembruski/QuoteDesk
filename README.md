# QuoteDesk

> A Django-based quotation management platform built around a real-world sales workflow.

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.2-092E20?logo=django&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black)
![Status](https://img.shields.io/badge/status-in%20development-blue)

**QuoteDesk** is a web-based sales quotation management system developed with **Python and Django**.

The project was designed around the real workflow of a swimming pool retailer, where quotations depend on configurable products such as pool models, heating systems, LED lighting, waterfalls and water-treatment solutions.

Its goal is not only to provide CRUD operations, but to model real business rules such as **historical pricing, quotation ownership, catalog configuration and role-based access**.

---

## Why this project?

Many quotation workflows are still managed through spreadsheets, messaging apps or manually edited documents.

QuoteDesk aims to centralize:

- Customers
- Product catalog
- Pool configurations
- Pricing
- Sales quotations
- Quotation status
- Seller ownership
- Historical commercial data

The application is being developed incrementally with a focus on **backend engineering, maintainability and real business requirements**.

---

# Engineering Highlights

## Historical pricing

One of the main business requirements is ensuring that an old quotation never changes when catalog prices are updated.

For example:

```text
Pool price when quotation was created:
R$ 18,000

Current catalog price:
R$ 21,000
```

The existing quotation must remain:

```text
R$ 18,000
```

To solve this, QuoteDesk stores **price snapshots** when a quotation is created.

```text
pool_price
heating_price
lighting_unit_price
waterfall_price
water_treatment_price
total_price
```

This preserves the integrity of historical commercial proposals.

---

## Relational domain modeling

The application models relationships between users, customers, quotations and catalog items.

```text
User
 │
 │ creates
 ▼
Quote
 │
 ├── Customer
 ├── PoolModel
 ├── HeatingOption
 ├── LED Lighting
 ├── Waterfall
 └── WaterTreatment
```

Examples of relationships:

- One customer can have multiple quotations.
- One seller can create multiple quotations.
- Each quotation belongs to the seller who created it.
- Catalog items can be reused across many quotations.

---

## Database constraints

The project uses database constraints to protect data consistency.

A pool model is uniquely identified by the combination:

```text
model + length + width
```

This allows:

```text
Castanha 8x2
Castanha 7x7
Bahamas 8x4
```

while preventing duplicated variants.

Heating configurations also use constraints to avoid duplicated combinations of type and capacity.

---

## Authentication and authorization

QuoteDesk uses Django's authentication system with a custom user model based on `AbstractUser`.

Current roles:

```text
ADMIN
SELLER
```

Planned permission rules:

**Admin**
- Full system access
- Catalog management
- User management
- Access to all quotations

**Seller**
- Customer management
- Quotation creation
- Access only to quotations created by that seller

This introduces both **role-based authorization** and **object-level access rules**.

---

# Tech Stack

## Backend

- Python
- Django 4.2
- Django ORM
- Django Authentication
- Custom `AbstractUser`
- Class-based and function-based views

## Database

- Relational data modeling
- Foreign keys
- Database constraints
- Decimal-based financial fields
- SQLite during initial development

Planned production database:

- PostgreSQL

## Frontend

- HTML5
- CSS3
- JavaScript
- Django Templates
- Responsive administrative interface

## Development Tools

- Git
- GitHub
- Pillow
- Python virtual environments

---

# Current Architecture

The project is organized into domain-focused Django apps:

```text
QuoteDesk/
│
├── accounts/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── templates/
│       └── accounts/
│
├── customer/
│   └── models.py
│
├── catalog/
│   └── models.py
│
├── quote/
│   └── models.py
│
├── dashboard/
│   ├── views.py
│   ├── urls.py
│   └── templates/
│       └── dashboard/
│
├── templates/
│   └── base.html
│
├── static/
│   └── img/
│
├── manage.py
└── requirements.txt
```

This structure separates responsibilities between:

```text
accounts  → authentication and users
customer  → customer data
catalog   → configurable products
quote     → quotation domain
dashboard → aggregated business information
```

---

# Domain Models

## User

Custom Django user containing:

```text
username
first_name
last_name
email
phone
photo
role
```

---

## Customer

Supports both individuals and companies.

```text
name
document (CPF/CNPJ)
phone
email
city
street
number
created_at
```

CPF/CNPJ values are unique to avoid duplicated customer records.

---

## PoolModel

Represents the available pool catalog.

```text
model
length
width
base_price
active
```

Different sizes of the same model can exist.

---

## HeatingOption

Supported heating types:

```text
Solar
Heat Exchanger
```

Each configuration contains:

```text
type
measure
price
active
```

The measurement depends on the heating system:

```text
Solar → meters
Heat exchanger → BTU
```

---

## Lighting

LED lighting uses unit pricing.

```text
unit_price
active
```

The quotation stores the selected quantity:

```text
LED total = quantity × unit_price
```

---

## Waterfall

```text
model
price
active
```

---

## WaterTreatment

Supported treatment systems:

```text
Chlorine
Ozone
```

Each option contains:

```text
type
price
active
```

---

## Quote

A quotation connects the main application domains.

```text
customer
created_by
pool
heating
lighting_quantity
waterfall
water_treatment
status
created_at
updated_at
```

Quotation statuses:

```text
DRAFT
SENT
APPROVED
REJECTED
```

Historical prices are stored independently from the catalog.

---

# Business Logic

The quotation total follows the structure:

```text
Pool price
+ Heating price
+ (LED quantity × LED unit price)
+ Waterfall price
+ Water treatment price
--------------------------------
Quotation total
```

Financial values use Django's `DecimalField` rather than floating-point values to maintain monetary precision.

---

# Interface

QuoteDesk currently includes:

- Custom visual identity
- Responsive login page
- Authenticated administrative area
- Reusable `base.html`
- Navigation sidebar
- User profile information
- Dashboard foundation

The design uses a consistent blue/navy visual system inspired by the swimming-pool industry.

---

# Development Status

🚧 **Currently under active development**

### Implemented

- [x] Django project architecture
- [x] Custom user model
- [x] Authentication
- [x] User roles
- [x] Profile image support
- [x] Customer domain model
- [x] Pool catalog model
- [x] Heating model
- [x] LED pricing model
- [x] Waterfall model
- [x] Water treatment model
- [x] Quotation model
- [x] Historical price fields
- [x] Quotation calculation logic
- [x] Login interface
- [x] Administrative base layout
- [x] Dashboard foundation

### Next milestones

- [ ] Customer registration
- [ ] Customer listing and search
- [ ] Catalog management screens
- [ ] Quotation creation workflow
- [ ] Automatic catalog price snapshot
- [ ] Automatic quotation calculation
- [ ] Quotation detail page
- [ ] Quotation editing
- [ ] Seller-level permissions
- [ ] Dashboard metrics
- [ ] PDF quotation generation

### Future improvements

- [ ] REST API
- [ ] OpenAPI / Swagger documentation
- [ ] Automated tests
- [ ] PostgreSQL
- [ ] Docker
- [ ] CI/CD
- [ ] Production deployment
- [ ] Quotation versioning
- [ ] Discounts
- [ ] Freight calculation
- [ ] Payment conditions
- [ ] Profit-margin analysis

---

# Planned Backend Evolution

As application complexity grows, business logic can be extracted into dedicated service classes.

Example:

```text
QuoteCreationService
QuotePricingService
QuotePDFService
```

This would keep responsibilities separated between:

```text
Models   → domain and persistence
Views    → HTTP flow
Services → business logic
Templates → presentation
```

Future API endpoints may also expose the same domain logic through Django REST Framework.

---

# Skills Demonstrated

This project demonstrates practical experience with:

- Python backend development
- Django architecture
- Relational database design
- Django ORM
- Foreign-key relationships
- Database constraints
- Authentication
- Authorization
- Object-level permissions
- Domain modeling
- Financial calculations
- Historical data preservation
- Business-rule implementation
- Modular Django applications
- Reusable templates
- Responsive interfaces
- Git and GitHub workflow

The project is intentionally based on a **real business scenario instead of a generic tutorial CRUD application**.

---

# Getting Started

Clone the repository:

```bash
git clone https://github.com/Kauanzembruski/QuoteDesk.git
cd QuoteDesk
```

Create a virtual environment:

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Apply migrations:

```bash
python manage.py migrate
```

Create an administrator:

```bash
python manage.py createsuperuser
```

Run the application:

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

---

# Security and Environment

Sensitive or environment-specific files are excluded from version control.

Examples:

```text
.env
db.sqlite3
media/
venv/
.venv/
__pycache__/
```

Production secrets will be managed through environment variables.

---

# Screenshots

> Screenshots will be added as the main application workflows are completed.

Suggested sections:

```text
Login
Dashboard
Customer Management
Catalog
Quotation Creation
Quotation Preview
```

---

# Project Goals

QuoteDesk is being developed to strengthen practical backend engineering skills through a real application that requires more than basic CRUD operations.

The main technical goals are:

- Build maintainable Django applications
- Design relational domains correctly
- Implement real business rules
- Protect historical commercial data
- Apply authentication and authorization
- Build APIs and automated tests
- Containerize and deploy a production-ready application

---

# Author

**Kauan Zembruski**

Software Developer focused on backend and web development.

**Main interests:** Python, Django, APIs, backend systems and automation.

GitHub: [@Kauanzembruski](https://github.com/Kauanzembruski)

---

# License

This project is currently being developed for portfolio, educational and private business purposes.
