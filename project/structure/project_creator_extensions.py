#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Méthodes supplémentaires pour la création de structures de projets
"""

import os
import json

def create_devops_project(project_path, technology_id, project_name):
    """Crée la structure d'un projet DevOps"""
    os.makedirs(os.path.join(project_path, "infrastructure"), exist_ok=True)
    os.makedirs(os.path.join(project_path, "scripts"), exist_ok=True)
    os.makedirs(os.path.join(project_path, "configs"), exist_ok=True)
    
    # Créer un fichier .gitignore
    with open(os.path.join(project_path, ".gitignore"), "w", encoding="utf-8") as f:
        f.write("# Fichiers locaux\n")
        f.write(".env\n")
        f.write("*.tfstate\n")
        f.write("*.tfstate.backup\n")
        f.write(".terraform/\n")
        f.write("*.tfvars\n")
        f.write("*.retry\n")
        f.write("node_modules/\n")
        
    # Créer un README.md
    with open(os.path.join(project_path, "README.md"), "w", encoding="utf-8") as f:
        f.write(f"# {project_name}\n\n")
        f.write("## Description\n\n")
        f.write("Infrastructure as Code et configuration DevOps.\n\n")
        f.write("## Structure du projet\n\n")
        f.write("- `infrastructure/` : Définitions d'infrastructure\n")
        f.write("- `scripts/` : Scripts d'automatisation\n")
        f.write("- `configs/` : Fichiers de configuration\n\n")
        
    if technology_id == "terraform":
        # Créer des fichiers pour Terraform
        with open(os.path.join(project_path, "main.tf"), "w", encoding="utf-8") as f:
            f.write("# Configuration principale Terraform\n\n")
            f.write("terraform {\n")
            f.write("  required_providers {\n")
            f.write("    aws = {\n")
            f.write("      source  = \"hashicorp/aws\"\n")
            f.write("      version = \"~> 4.0\"\n")
            f.write("    }\n")
            f.write("  }\n")
            f.write("}\n\n")
            f.write("provider \"aws\" {\n")
            f.write("  region = var.aws_region\n")
            f.write("}\n\n")
            f.write("# Modules\n")
            f.write("module \"vpc\" {\n")
            f.write("  source = \"./infrastructure/vpc\"\n")
            f.write("}\n\n")
            
        with open(os.path.join(project_path, "variables.tf"), "w", encoding="utf-8") as f:
            f.write("variable \"aws_region\" {\n")
            f.write("  description = \"Région AWS à utiliser\"\n")
            f.write("  type        = string\n")
            f.write("  default     = \"eu-west-3\"\n")
            f.write("}\n\n")
            
        # Créer un module VPC
        os.makedirs(os.path.join(project_path, "infrastructure", "vpc"), exist_ok=True)
        with open(os.path.join(project_path, "infrastructure", "vpc", "main.tf"), "w", encoding="utf-8") as f:
            f.write("# Définition du VPC\n\n")
            f.write("resource \"aws_vpc\" \"main\" {\n")
            f.write("  cidr_block = var.vpc_cidr\n")
            f.write("  tags = {\n")
            f.write("    Name = var.vpc_name\n")
            f.write("  }\n")
            f.write("}\n\n")
            
        with open(os.path.join(project_path, "infrastructure", "vpc", "variables.tf"), "w", encoding="utf-8") as f:
            f.write("variable \"vpc_cidr\" {\n")
            f.write("  description = \"CIDR block pour le VPC\"\n")
            f.write("  type        = string\n")
            f.write("  default     = \"10.0.0.0/16\"\n")
            f.write("}\n\n")
            f.write("variable \"vpc_name\" {\n")
            f.write("  description = \"Nom du VPC\"\n")
            f.write("  type        = string\n")
            f.write(f"  default     = \"{project_name}-vpc\"\n")
            f.write("}\n")
            
    elif technology_id == "docker":
        # Créer des fichiers pour Docker
        with open(os.path.join(project_path, "docker-compose.yml"), "w", encoding="utf-8") as f:
            f.write("version: '3.8'\n\n")
            f.write("services:\n")
            f.write("  app:\n")
            f.write("    build:\n")
            f.write("      context: .\n")
            f.write("      dockerfile: Dockerfile\n")
            f.write("    ports:\n")
            f.write("      - \"8080:8080\"\n")
            f.write("    volumes:\n")
            f.write("      - ./:/app\n")
            f.write("    environment:\n")
            f.write("      - NODE_ENV=development\n")
            
        with open(os.path.join(project_path, "Dockerfile"), "w", encoding="utf-8") as f:
            f.write("FROM node:16-alpine\n\n")
            f.write("WORKDIR /app\n\n")
            f.write("COPY package*.json ./\n\n")
            f.write("RUN npm install\n\n")
            f.write("COPY . .\n\n")
            f.write("EXPOSE 8080\n\n")
            f.write("CMD [\"npm\", \"start\"]\n")

def create_microservices_project(project_path, technology_id, project_name):
    """Crée la structure d'un projet microservices"""
    os.makedirs(os.path.join(project_path, "services"), exist_ok=True)
    os.makedirs(os.path.join(project_path, "gateway"), exist_ok=True)
    os.makedirs(os.path.join(project_path, "common"), exist_ok=True)
    os.makedirs(os.path.join(project_path, "infrastructure"), exist_ok=True)
    
    # Créer un fichier docker-compose.yml
    with open(os.path.join(project_path, "docker-compose.yml"), "w", encoding="utf-8") as f:
        f.write("version: '3.8'\n\n")
        f.write("services:\n")
        f.write("  gateway:\n")
        f.write("    build: ./gateway\n")
        f.write("    ports:\n")
        f.write("      - \"8080:8080\"\n")
        f.write("    depends_on:\n")
        f.write("      - service-a\n")
        f.write("      - service-b\n\n")
        f.write("  service-a:\n")
        f.write("    build: ./services/service-a\n")
        f.write("    ports:\n")
        f.write("      - \"8081:8081\"\n\n")
        f.write("  service-b:\n")
        f.write("    build: ./services/service-b\n")
        f.write("    ports:\n")
        f.write("      - \"8082:8082\"\n\n")
        
    # Créer un README.md
    with open(os.path.join(project_path, "README.md"), "w", encoding="utf-8") as f:
        f.write(f"# {project_name}\n\n")
        f.write("## Architecture microservices\n\n")
        f.write("Ce projet utilise une architecture microservices.\n\n")
        f.write("## Structure du projet\n\n")
        f.write("- `services/` : Services individuels\n")
        f.write("- `gateway/` : API Gateway\n")
        f.write("- `common/` : Code partagé entre les services\n")
        f.write("- `infrastructure/` : Configuration d'infrastructure\n\n")
        
    # Créer des services de base
    os.makedirs(os.path.join(project_path, "services", "service-a"), exist_ok=True)
    os.makedirs(os.path.join(project_path, "services", "service-b"), exist_ok=True)
    
    if technology_id == "spring-cloud":
        # Créer des fichiers pour Spring Cloud
        with open(os.path.join(project_path, "pom.xml"), "w", encoding="utf-8") as f:
            f.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
            f.write("<project xmlns=\"http://maven.apache.org/POM/4.0.0\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n")
            f.write("         xsi:schemaLocation=\"http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd\">\n")
            f.write("    <modelVersion>4.0.0</modelVersion>\n")
            f.write("    <parent>\n")
            f.write("        <groupId>org.springframework.boot</groupId>\n")
            f.write("        <artifactId>spring-boot-starter-parent</artifactId>\n")
            f.write("        <version>2.7.0</version>\n")
            f.write("        <relativePath/>\n")
            f.write("    </parent>\n")
            f.write(f"    <groupId>com.example</groupId>\n")
            f.write(f"    <artifactId>{project_name.lower().replace(' ', '-')}</artifactId>\n")
            f.write("    <version>0.0.1-SNAPSHOT</version>\n")
            f.write(f"    <name>{project_name}</name>\n")
            f.write(f"    <description>Projet microservices {project_name}</description>\n")
            f.write("    <packaging>pom</packaging>\n\n")
            f.write("    <modules>\n")
            f.write("        <module>gateway</module>\n")
            f.write("        <module>services/service-a</module>\n")
            f.write("        <module>services/service-b</module>\n")
            f.write("        <module>common</module>\n")
            f.write("    </modules>\n\n")
            f.write("    <properties>\n")
            f.write("        <java.version>17</java.version>\n")
            f.write("        <spring-cloud.version>2021.0.3</spring-cloud.version>\n")
            f.write("    </properties>\n\n")
            f.write("    <dependencyManagement>\n")
            f.write("        <dependencies>\n")
            f.write("            <dependency>\n")
            f.write("                <groupId>org.springframework.cloud</groupId>\n")
            f.write("                <artifactId>spring-cloud-dependencies</artifactId>\n")
            f.write("                <version>${spring-cloud.version}</version>\n")
            f.write("                <type>pom</type>\n")
            f.write("                <scope>import</scope>\n")
            f.write("            </dependency>\n")
            f.write("        </dependencies>\n")
            f.write("    </dependencyManagement>\n\n")
            f.write("</project>\n")
            
    elif technology_id == "nestjs":
        # Créer des fichiers pour NestJS
        with open(os.path.join(project_path, "package.json"), "w", encoding="utf-8") as f:
            package_json = {
                "name": project_name.lower().replace(' ', '-'),
                "version": "0.0.1",
                "description": "Architecture microservices avec NestJS",
                "private": True,
                "scripts": {
                    "start": "npm run start:dev",
                    "start:dev": "concurrently \"npm run start:gateway\" \"npm run start:service-a\" \"npm run start:service-b\"",
                    "start:gateway": "cd gateway && npm run start:dev",
                    "start:service-a": "cd services/service-a && npm run start:dev",
                    "start:service-b": "cd services/service-b && npm run start:dev",
                    "install:all": "npm install && npm run install:gateway && npm run install:service-a && npm run install:service-b",
                    "install:gateway": "cd gateway && npm install",
                    "install:service-a": "cd services/service-a && npm install",
                    "install:service-b": "cd services/service-b && npm install"
                },
                "devDependencies": {
                    "concurrently": "^7.2.1"
                }
            }
            json.dump(package_json, f, indent=2)

def create_cms_project(project_path, technology_id, project_name):
    """Crée la structure d'un projet CMS"""
    if technology_id == "wordpress":
        os.makedirs(os.path.join(project_path, "wp-content"), exist_ok=True)
        os.makedirs(os.path.join(project_path, "wp-content", "themes"), exist_ok=True)
        os.makedirs(os.path.join(project_path, "wp-content", "plugins"), exist_ok=True)
        
        # Créer un fichier docker-compose.yml pour WordPress
        with open(os.path.join(project_path, "docker-compose.yml"), "w", encoding="utf-8") as f:
            f.write("version: '3.8'\n\n")
            f.write("services:\n")
            f.write("  wordpress:\n")
            f.write("    image: wordpress:latest\n")
            f.write("    ports:\n")
            f.write("      - \"8000:80\"\n")
            f.write("    environment:\n")
            f.write("      WORDPRESS_DB_HOST: db\n")
            f.write("      WORDPRESS_DB_USER: wordpress\n")
            f.write("      WORDPRESS_DB_PASSWORD: wordpress\n")
            f.write("      WORDPRESS_DB_NAME: wordpress\n")
            f.write("    volumes:\n")
            f.write("      - ./wp-content:/var/www/html/wp-content\n")
            f.write("    depends_on:\n")
            f.write("      - db\n\n")
            f.write("  db:\n")
            f.write("    image: mysql:5.7\n")
            f.write("    environment:\n")
            f.write("      MYSQL_DATABASE: wordpress\n")
            f.write("      MYSQL_USER: wordpress\n")
            f.write("      MYSQL_PASSWORD: wordpress\n")
            f.write("      MYSQL_RANDOM_ROOT_PASSWORD: '1'\n")
            f.write("    volumes:\n")
            f.write("      - db_data:/var/lib/mysql\n\n")
            f.write("volumes:\n")
            f.write("  db_data:\n")
            
        # Créer un fichier README.md
        with open(os.path.join(project_path, "README.md"), "w", encoding="utf-8") as f:
            f.write(f"# {project_name} - Site WordPress\n\n")
            f.write("## Installation\n\n")
            f.write("1. Assurez-vous que Docker et Docker Compose sont installés\n")
            f.write("2. Exécutez `docker-compose up -d`\n")
            f.write("3. Accédez à http://localhost:8000 pour configurer WordPress\n\n")
            f.write("## Structure du projet\n\n")
            f.write("- `wp-content/themes/` : Thèmes personnalisés\n")
            f.write("- `wp-content/plugins/` : Plugins personnalisés\n")
            
    elif technology_id == "strapi":
        # Créer des fichiers pour Strapi
        with open(os.path.join(project_path, "package.json"), "w", encoding="utf-8") as f:
            package_json = {
                "name": project_name.lower().replace(' ', '-'),
                "private": True,
                "version": "0.1.0",
                "description": f"Projet CMS Strapi - {project_name}",
                "scripts": {
                    "develop": "strapi develop",
                    "start": "strapi start",
                    "build": "strapi build",
                    "strapi": "strapi"
                },
                "dependencies": {
                    "@strapi/strapi": "4.10.5",
                    "@strapi/plugin-users-permissions": "4.10.5",
                    "@strapi/plugin-i18n": "4.10.5",
                    "better-sqlite3": "8.0.1"
                },
                "engines": {
                    "node": ">=14.19.1 <=18.x.x",
                    "npm": ">=6.0.0"
                },
                "license": "MIT"
            }
            json.dump(package_json, f, indent=2)
            
        # Créer un fichier README.md
        with open(os.path.join(project_path, "README.md"), "w", encoding="utf-8") as f:
            f.write(f"# {project_name} - CMS Strapi\n\n")
            f.write("## Installation\n\n")
            f.write("```bash\n")
            f.write("# Installation des dépendances\n")
            f.write("npm install\n\n")
            f.write("# Démarrage du serveur de développement\n")
            f.write("npm run develop\n")
            f.write("```\n\n")
            f.write("## Accès\n\n")
            f.write("- Interface d'administration : http://localhost:1337/admin\n")
            f.write("- API : http://localhost:1337/api\n")
