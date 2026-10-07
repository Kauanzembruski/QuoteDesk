# QuoteDesk

A web-based quotation management system built with **Python and Django**, designed around the real workflow of a swimming pool retailer.

QuoteDesk centralizes customers, product catalog, configurable pool options, pricing and sales quotations in a single application.

The project focuses on **backend development, relational modeling, authentication, authorization and real business rules**.

---

## Tech Stack

### Backend
- Python
- Django 4.2
- Django ORM
- Django Authentication
- Custom `AbstractUser`

### Database
- Relational data modeling
- Foreign keys
- Database constraints
- `DecimalField` for financial values
- SQLite during development
- PostgreSQL planned for production

### Frontend
- HTML5
- CSS3
- JavaScript
- Django Templates

### Tools
- Git
- GitHub
- Pillow

---

## Main Features

- Custom authentication
- User roles: `ADMIN` and `SELLER`
- Customer management
- Pool catalog
- Heating options
- LED lighting pricing
- Waterfall catalog
- Water treatment options
- Sales quotations
- Quotation status workflow
- Historical price preservation
- Administrative dashboard structure

---

## Business Rules

### Historical pricing

Catalog prices can change, but existing quotations must keep the original values.

Example:

```text
Pool price when quotation was created:
R$ 18,000

Current catalog price:
R$ 21,000
```

The quotation still keeps:

```text
R$ 18,000
```

QuoteDesk stores price snapshots such as:

```text
pool_price
heating_price
lighting_unit_price
waterfall_price
water_treatment_price
total_price
```

This protects the history of commercial proposals.

---

### Seller ownership

Each quotation is associated with the user who created it.

Planned access rules:

```text
ADMIN
→ full access

SELLER
→ create customers
→ create quotations
→ access only their own quotations
```

---

## Domain Model

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

A customer can have multiple quotations.

A seller can create multiple quotations.

---

## Quotation Calculation

```text
Pool
+ Heating
+ LED quantity × LED unit price
+ Waterfall
+ Water treatment
----------------------------
Quotation total
```

Financial values use `DecimalField` to avoid floating-point precision issues.

---

## Project Structure

```text
QuoteDesk/
│
├── accounts/
├── customer/
├── catalog/
├── quote/
├── dashboard/
├── templates/
├── static/
├── manage.py
└── requirements.txt
```

Each Django app has a clear responsibility:

```text
accounts  → authentication and users
customer  → customer data
catalog   → products and configurations
quote     → quotation business logic
dashboard → business overview
```

---

## Current Status

🚧 **In active development**

### Implemented

- [x] Custom user model
- [x] Authentication
- [x] User roles
- [x] Customer model
- [x] Pool catalog
- [x] Heating configuration
- [x] LED pricing
- [x] Waterfall model
- [x] Water treatment model
- [x] Quotation model
- [x] Historical pricing
- [x] Quotation calculation
- [x] Login interface
- [x] Administrative layout
- [x] Dashboard foundation

### Next Steps

- [ ] Customer CRUD
- [ ] Catalog management
- [ ] Quotation creation workflow
- [ ] Automatic price snapshot
- [ ] Seller permissions
- [ ] Dashboard metrics
- [ ] PDF quotation generation
- [ ] REST API
- [ ] Automated tests
- [ ] PostgreSQL
- [ ] Docker
- [ ] CI/CD
- [ ] Production deployment

---

## Skills Demonstrated

- Python backend development
- Django architecture
- Relational database modeling
- Django ORM
- Authentication and authorization
- Object-level permissions
- Business-rule implementation
- Financial calculations
- Historical data preservation
- Modular application design
- Git and GitHub workflow

---

## Getting Started

```bash
git clone https://github.com/Kauanzembruski/QuoteDesk.git
cd QuoteDesk
```

Create and activate a virtual environment:

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
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

Run:

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

---

## About the Project

QuoteDesk is based on a **real business workflow**, not a generic tutorial CRUD project.

The goal is to build a maintainable commercial system while applying backend concepts commonly required in real-world Django applications.

---

## Author

**Kauan Zembruski**

Software Developer focused on backend and web development.

GitHub: [@Kauanzembruski](https://github.com/Kauanzembruski)
