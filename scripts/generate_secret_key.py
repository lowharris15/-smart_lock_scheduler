#!/usr/bin/env python3
import os
import secrets

def generate_secret_key(length=32):
    """Generate a secure random key suitable for Flask's SECRET_KEY"""
    return secrets.token_hex(length)

if __name__ == "__main__":
    secret_key = generate_secret_key()
    print(f"Generated SECRET_KEY: {secret_key}")
    print("\nAdd this to your .env file as:\nSECRET_KEY={secret_key}")
    
    # Optionally update .env file if it exists
    env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    if os.path.exists(env_file):
        try:
            with open(env_file, 'r') as f:
                env_content = f.read()
                
            if 'SECRET_KEY=' in env_content:
                print("\nAn existing SECRET_KEY was found in your .env file.")
                choice = input("Do you want to replace it? (y/n): ")
                if choice.lower() != 'y':
                    print("Operation cancelled. Your .env file was not modified.")
                    exit(0)
                    
                # Replace existing SECRET_KEY
                env_lines = env_content.split('\n')
                for i, line in enumerate(env_lines):
                    if line.startswith('SECRET_KEY='):
                        env_lines[i] = f'SECRET_KEY={secret_key}'
                        break
                        
                with open(env_file, 'w') as f:
                    f.write('\n'.join(env_lines))
                print("Your .env file has been updated with the new SECRET_KEY.")
            else:
                # Append SECRET_KEY to the file
                with open(env_file, 'a') as f:
                    f.write(f"\nSECRET_KEY={secret_key}\n")
                print("SECRET_KEY has been appended to your .env file.")
        except Exception as e:
            print(f"Error updating .env file: {str(e)}")
            print("Please manually add the SECRET_KEY to your .env file.")
    else:
        print("No .env file found. Please create one and add the SECRET_KEY manually.") 