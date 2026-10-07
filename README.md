# QuoteDesk

QuoteDesk is a web-based sales quotation management system designed initially for a swimming pool retailer.

The platform centralizes customers, pool models, accessories, pricing and quotations in a single application, helping sales teams create and manage commercial proposals in a more organized and reliable way.

The project is being developed with **Python, Django and relational data modeling**, with a strong focus on real-world business rules, maintainability and backend development practices.

> This project is currently under active development. New features and improvements will be added progressively.

---

## Overview

Swimming pool quotations can involve several configurable components, such as:

- Pool model and dimensions
- Heating systems
- LED lighting
- Waterfalls
- Water treatment systems
- Customer information
- Pricing and quotation status

QuoteDesk was created to centralize this process and avoid manually managing quotation information across different files or tools.

The system is designed around a real business use case and may eventually be used in an actual commercial operation.

---

## Current Features

### Authentication

- Custom Django user model
- Username-based authentication
- User profile information
- Profile picture
- User roles
- Protected authenticated pages

Currently supported roles:

- `ADMIN`
- `SELLER`

Administrators are intended to have full system access, while sellers will primarily work with customers and their own quotations.

---

### Customer Management

Customer records support both individuals and companies.

Stored information includes:

- Name
- CPF / CNPJ
- Phone
- Email
- City
- Street
- Address number
- Creation date

Customer documents are unique to avoid duplicate registrations.

---

### Pool Catalog

Pool models can be registered with:

- Model name
- Length
- Width
- Base price
- Active / inactive status

Different dimensions of the same pool model can coexist.

Example:

```text
Castanha 8x2
Castanha 7x7
Bahamas 8x4
```

A database constraint prevents duplicate combinations of:

```text
model + length + width
```

---

### Heating Options

Heating systems currently support:

- Solar heating
- Heat exchangers

Each heating option has:

- Type
- Capacity / measurement
- Price
- Active status

Examples:

```text
Solar - 20 m
Heat exchanger - 60000 BTU
```

The measurement unit is inferred from the heating type.

---

### LED Lighting

LED lighting uses a unit-based pricing model.

The catalog stores:

```text
unit_price
```

The quotation stores the selected quantity and calculates the total according to:

```text
LED total = quantity × unit price
```

---

### Waterfalls

Waterfall products can be registered with:

- Model
- Price
- Active status

---

### Water Treatment

Supported water treatment options include:

- Chlorine
- Ozone

Each treatment option has its own price and availability status.

---

### Quotations

A quotation can currently reference:

- Customer
- Seller
- Pool model
- Heating option
- LED quantity
- Waterfall
- Water treatment
- Status
- Creation date
- Update date

Available quotation statuses:

```text
Draft
Sent
Approved
Rejected
```

---

## Historical Pricing

One important business rule in QuoteDesk is preserving quotation history.

Catalog prices may change over time, but an existing quotation should not change when that happens.

For example:

```text
Pool price today:
R$ 18,000

Pool price after an update:
R$ 21,000
```

A quotation created before the update must continue showing:

```text
R$ 18,000
```

For this reason, QuoteDesk stores price snapshots directly inside each quotation.

Examples:

```text
pool_price
heating_price
lighting_unit_price
waterfall_price
water_treatment_price
total_price
```

This keeps historical commercial proposals consistent even when catalog prices are updated.

---

## Quotation Calculation

The quotation model contains business logic for calculating the final price.

Conceptually:

```text
Pool
+ Heating
+ LED quantity × LED unit price
+ Waterfall
+ Water treatment
----------------------------
Quotation total
```

This logic is kept close to the quotation domain instead of being handled only in the presentation layer.

---

## Dashboard

QuoteDesk includes an authenticated administrative interface.

The current layout provides the foundation for:

- Dashboard
- Customers
- Catalog
- Quotations
- User information
- Logout

The dashboard will progressively include business metrics such as:

- Quotations created
- Customers registered
- Approved quotations
- Approved sales value
- Recent quotations

---

## UI

The interface uses a custom QuoteDesk visual identity inspired by the swimming pool industry.

The design currently includes:

- Custom QuoteDesk logo
- Responsive login page
- Administrative sidebar
- User profile area
- Reusable base template
- Consistent blue and navy color palette

---

## Tech Stack

### Backend

- Python
- Django 4.2

### Database

- Django ORM
- Relational database structure

### Frontend

- HTML5
- CSS3
- Django Templates
- JavaScript

### Authentication

- Django Authentication System
- Custom `AbstractUser`

### Other

- Pillow for image handling
- Git
- GitHub

---

## Project Structure

A simplified version of the current architecture:

```text
QuoteDesk/
│
├── accounts/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── templates/
│       └── accounts/
│           └── login.html
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
│           └── dashboard.html
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

The structure may evolve as the project grows.

---

## Domain Model

At a high level, the application follows this structure:

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

Each quotation keeps its own historical price information.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/Kauanzembruski/QuoteDesk.git
```

Enter the project directory:

```bash
cd QuoteDesk
```

Create a virtual environment:

### Windows

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Database Setup

Apply migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

Create an administrator:

```bash
python manage.py createsuperuser
```

Run the development server:

```bash
python manage.py runserver
```

Then open:

```text
http://127.0.0.1:8000/
```

---

## Environment Configuration

Sensitive information should not be committed to GitHub.

The project `.gitignore` should exclude files such as:

```text
.env
db.sqlite3
media/
venv/
.venv/
__pycache__/
```

Future production configuration will use environment variables for secrets and deployment settings.

---

## Roadmap

QuoteDesk is still evolving.

Planned features include:

- [x] Custom authentication
- [x] Custom user roles
- [x] Customer data model
- [x] Pool catalog modeling
- [x] Heating configuration
- [x] LED pricing model
- [x] Waterfall catalog
- [x] Water treatment catalog
- [x] Quotation data model
- [x] Historical quotation pricing
- [x] Login interface
- [x] Administrative base layout
- [ ] Customer registration interface
- [ ] Customer list and search
- [ ] Catalog management interface
- [ ] Quotation creation form
- [ ] Automatic catalog price snapshot
- [ ] Automatic quotation total calculation during creation
- [ ] Quotation detail page
- [ ] Quotation editing
- [ ] Seller-specific quotation permissions
- [ ] Dashboard with real metrics
- [ ] PDF quotation generation
- [ ] Printable commercial proposal
- [ ] Quotation versioning
- [ ] Payment conditions
- [ ] Discounts
- [ ] Freight calculation
- [ ] Profit margin calculation
- [ ] Search and filtering
- [ ] REST API
- [ ] API documentation
- [ ] Automated tests
- [ ] Docker support
- [ ] PostgreSQL production environment
- [ ] CI/CD
- [ ] Production deployment

---

## Future Architecture

As the project grows, some business rules may be moved into dedicated service layers.

For example:

```text
QuoteCreationService
QuotePricingService
QuotePDFService
```

This will help keep views, models and business logic separated as complexity increases.

---

## Main Learning Goals

QuoteDesk is also being developed as a portfolio project focused on real-world backend development.

The project explores concepts such as:

- Django architecture
- Relational database modeling
- Foreign keys
- Database constraints
- Authentication
- Authorization
- Object-level permissions
- Business rules
- Historical data
- Financial calculations
- Reusable templates
- Domain modeling
- Clean project organization
- Git and GitHub workflow

---

## Why QuoteDesk?

Instead of being a generic tutorial CRUD project, QuoteDesk is based on a real commercial workflow.

The goal is to develop software capable of solving an actual business problem while progressively applying professional backend development practices.

---

## Status

🚧 **In active development**

The project currently has its initial domain modeling, authentication system and interface foundation implemented.

The next major milestone is completing the customer and quotation workflows.

---

## Author

**Kauan Zembruski**

Software Developer

GitHub: [@Kauanzembruski](https://github.com/Kauanzembruski)

---

## License

This project is currently intended for educational, portfolio and private business development purposes.