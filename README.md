# Blog-Lite-V2

Blog-Lite is a multi-user application designed for uploading blogs with images. It allows users to create and share their posts with others. Each post consists of an ID, title, caption/description, image URL, and timestamp. Users can follow other users within the app and have their own feed displaying blogs from the users they follow.

## Terminology

- Social Platform: The platform where users can connect, share blogs, and interact with each other.
- Profile: The user's basic information, including stats and a list of their blogs.
- Feed: A curated list of blogs uploaded by the users that the current user follows.
- Archive (optional): A feature that allows users to make their blogs private or hidden from others.

## Features

- Multi-user functionality: Users can create accounts and post multiple blogs.
- User profile: Each user has a username, password, number of followers, and number of posts.
- Personalized feed: The system automatically displays blogs from the users a user follows in a specific sequence.
- Timestamp-based sorting: The recommended order of blogs in a user's feed is based on the timestamp of the blogs.
- Image uploads: Users can upload blogs with accompanying images.

## Frameworks Used

- Flask: Used for application code development.
- Jinja2 templates + Bootstrap: Used for HTML generation and styling.
- SQLite: Used for data storage.

## How to Use

To set up and use Blog-Lite, follow these steps:

1. Clone the repository to your local machine.
2. Install the required dependencies and frameworks.
3. Set up the SQLite database for data storage.
4. Configure the Flask application settings.
5. Run the application on a standalone platform like replict.com or set up a server for deployment.
6. Create an account and start exploring the features of Blog-Lite.
7. Customize your profile, follow other users, and start posting blogs.
8. Check your personalized feed to discover blogs from users you follow.
9. Use the optional archive feature to manage the privacy of your blogs.

Please note that this project can be demoed on a standalone platform like replict.com, eliminating the need for additional server setup for database and frontend management.

We hope you enjoy using Blog-Lite to share your thoughts, connect with others, and explore a vibrant community of bloggers.
