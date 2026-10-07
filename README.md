# QuoteDesk

<p align="center">
  <img src="static/img/login.png" alt="QuoteDesk Logo" width="220">
</p>

<p align="center">
  A web-based quotation management system built with <strong>Python and Django</strong>,
  designed around the real workflow of a swimming pool retailer.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/Django-4.2-092E20?style=for-the-badge&logo=django&logoColor=white">
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white">
  <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white">
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-In%20Development-0D8DF0?style=flat-square">
  <img src="https://img.shields.io/badge/Architecture-Modular%20Django-0B2545?style=flat-square">
  <img src="https://img.shields.io/badge/Focus-Backend%20Engineering-6C63FF?style=flat-square">
</p>

---

## 🚀 About the Project

QuoteDesk centralizes customers, product catalog, configurable pool options, pricing and sales quotations in a single application.

The project focuses on:

- Backend development
- Relational database modeling
- Authentication and authorization
- Business-rule implementation
- Historical pricing
- Modular Django architecture

---

## 🛠 Tech Stack

### Backend

<p>
  <img src="https://skillicons.dev/icons?i=python,django" />
</p>

- Python
- Django 4.2
- Django ORM
- Django Authentication
- Custom `AbstractUser`

### Database

<p>
  <img src="https://skillicons.dev/icons?i=sqlite,postgres" />
</p>

- Relational data modeling
- Foreign keys
- Database constraints
- `DecimalField` for financial values
- SQLite in development
- PostgreSQL planned for production

### Frontend

<p>
  <img src="https://skillicons.dev/icons?i=html,css,js" />
</p>

- HTML5
- CSS3
- JavaScript
- Django Templates

### Tools

<p>
  <img src="https://skillicons.dev/icons?i=git,github,vscode" />
</p>

- Git
- GitHub
- Pillow
- Virtual environments

---

## ✨ Main Features

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
- Administrative dashboard

---

## 🧠 Key Business Rule

### Historical Pricing

Catalog prices may change, but existing quotations must keep the original values.

```text
Quotation pool price:
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

This preserves the integrity of historical commercial proposals.

---

## 🔐 Access Control

```text
ADMIN
→ full access

SELLER
→ customer management
→ create quotations
→ access only their own quotations
```

This introduces both role-based authorization and object-level access rules.

---

## 🧩 Domain Model

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

---

## 🧮 Quotation Calculation

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

## 🗂 Project Structure

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

```text
accounts  → authentication and users
customer  → customer data
catalog   → products and configurations
quote     → quotation business logic
dashboard → business overview
```

---

## 📌 Development Status

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

## 💼 Skills Demonstrated

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

## ⚙️ Getting Started

```bash
git clone https://github.com/Kauanzembruski/QuoteDesk.git
cd QuoteDesk
```

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

Run the project:

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

---

## 📷 Screenshots

> Screenshots will be added as the main workflows are completed.

Planned sections:

- Login
- Dashboard
- Customer Management
- Catalog
- Quotation Creation
- Quotation Preview

---

## 👨‍💻 Author

**Kauan Zembruski**

Software Developer focused on backend and web development.

GitHub: [@Kauanzembruski](https://github.com/Kauanzembruski)
