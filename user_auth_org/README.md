Install dependencies:

pip install -r requirements.txt

Apply database migrations:

python manage.py migrate

Run the development server:

python manage.py runserver

The application will be accessible at http://localhost:8000.

Endpoints
User Registration
POST /auth/register/

Registers a new user and creates a default organization.

Request Body:

{ "firstName": "string", "lastName": "string", "email": "string", "password": "string", "phone": "string" }

Successful Response:

{ "status": "success", "message": "Registration successful", "data": { "accessToken": "eyJh...", "user": { "userId": "string", "firstName": "string", "lastName": "string", "email": "string", "phone": "string" } } }

User Login
POST /auth/login/

Logs in a user with valid credentials.

Request Body:

{ "email": "string", "password": "string" }

Successful Response:

{ "status": "success", "message": "Login successful", "data": { "accessToken": "eyJh...", "user": { "userId": "string", "firstName": "string", "lastName": "string", "email": "string", "phone": "string" } } }

User Detail
GET /api/users/int:id/

Retrieves the details of a specific user.

Successful Response:

{ "status": "success", "message": "User details retrieved", "data": { "userId": "string", "firstName": "string", "lastName": "string", "email": "string", "phone": "string" } }

Organisation List
GET /api/organisations/

Retrieves a list of organizations the logged-in user belongs to or created.

Successful Response:

{ "status": "success", "message": "Organisations retrieved", "data": { "organisations": [ { "orgId": "string", "name": "string", "description": "string" } ] } }

Organisation Detail
GET /api/organisations/int:orgId/

Retrieves the details of a specific organization.

Successful Response:

{ "status": "success", "message": "Organisation details retrieved", "data": { "orgId": "string", "name": "string", "description": "string" } }

Organisation Create
POST /api/organisationsCreate/

Creates a new organization.

Request Body:

{ "name": "string", "description": "string" }

Successful Response:

{ "status": "success", "message": "Organisation created successfully", "data": { "orgId": "string", "name": "string", "description": "string" } }

Add User to Organisation
POST /api/organisations/int:orgId/users/

Adds a user to a specific organization.

Request Body:

{ "userId": "string" }

Successful Response:

{ "status": "success", "message": "User added to organisation successfully" }

Token Obtain
POST /api/token/

Obtain JWT token for authentication.

Request Body:

{ "username": "string", "password": "string" }

Successful Response:

{ "access": "string", "refresh": "string" }
