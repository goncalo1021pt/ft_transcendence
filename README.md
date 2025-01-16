# ft_transcendence
Final project of the 42 Common Core

django tldr:

🔹 **Models** (Data Containers):
```python
# Like C++ classes that map to database tables
class User(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
```

🔹 **Forms** (Input Handling/Validation):
```python
# Like std::cin + validation
class LoginForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(min_length=8)
```

🔹 **Views** (Request Handlers):
```python
# Like API endpoints that process requests
def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # Save to database
            return redirect('success')
    return render(request, 'login.html', {'form': form})
```

Flow:
1. URL routes to View
2. View processes request
3. Form validates input
4. Model handles data storage
5. View returns response

Think:
- Models = Database tables
- Forms = Input validation
- Views = Request processors


## PostgreSQL TLDR

### Basic Commands
```bash
# Login to PostgreSQL
psql -U postgres                    # As postgres user
psql -U django_user -d django_db    # As specific user/database
PGPASSWORD=mypass psql -U user -d db # With password

# Inside PSQL
\du          # List users and roles
\l           # List databases
\dt          # List tables in current db
\d tablename # Describe table structure
\c dbname    # Connect to database
\q           # Quit
\x           # Toggle expanded display
\timing      # Toggle query timing

# SQL Queries 
SELECT * FROM tablename;          # Show all rows
SELECT * FROM tablename LIMIT 5;  # Show first 5 rows
SELECT column1, column2 FROM tablename; # Show specific columns


### 1. **Component-Based Design**
Component-based design involves breaking down the user interface into reusable, self-contained components. Each component encapsulates its structure, style, and behavior.

#### Example:
- **BaseComponent**: A base class for all components, handling common functionality like fetching templates and lifecycle methods (

onIni

, 

onDestroy

).
- **UserPage**: A specific component extending 

BaseComponent

, representing the user page.

### 2. **Modular JavaScript**
Modular JavaScript involves organizing code into separate files (modules) that can be imported and used where needed. This improves code maintainability and reusability.

#### Example:
- **index.js**: The main entry point, initializing the router and subscribing components.
- **UserPage.js**: Defines the 

UserPage

 component.

### 3. **Custom Elements**
Custom Elements are a Web Components standard that allows you to define new HTML elements. These elements can encapsulate their behavior and style, making them reusable across the application.

#### Example:
- **BaseComponent**: Defined as a custom element using 

customElements.define('base-component', BaseComponent)

.
- **UserPage**: Defined as a custom element using 

customElements.define('user-page', UserPage)

.

### 4. **Router**
A simple router to handle navigation between different components/pages. It subscribes components to specific routes and loads them as needed.

#### Example:
- **Router**: Manages navigation and dynamically loads components based on the URL.

### 5. **Django Backend**
Django is used as the backend framework to handle server-side logic, database interactions, and rendering initial HTML templates.

#### Example:
- **Views**: Handle HTTP requests and render templates.
- **Forms**: Handle user input and validation.
- **Models**: Define the database schema.

### 6. **Integration**
The integration of Django and modern JavaScript allows for a dynamic and interactive single-page application (SPA) while leveraging Django's robust backend capabilities.

#### Example:
- **index.html**: The main HTML template, loading JavaScript modules and initializing the application.
- **router.js**: Manages the dynamic loading of content based on navigation.

### Summary
This approach combines the strengths of Django for backend development with modern JavaScript techniques for frontend development. It results in a modular, maintainable, and interactive web application. The key elements are:
- **Component-Based Design**: Reusable and self-contained UI components.
- **Modular JavaScript**: Organized and maintainable code.
- **Custom Elements**: Encapsulated behavior and style.
- **Router**: Dynamic navigation and content loading.
- **Django Backend**: Robust server-side logic and database management.