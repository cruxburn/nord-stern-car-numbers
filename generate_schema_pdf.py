#!/usr/bin/env python3
"""
Database Schema PDF Generator
Generates a professional PDF document of the Nord Stern Car Numbers database schema
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import os
from datetime import datetime

def create_schema_pdf():
    """Generate the database schema PDF"""
    
    # Create PDF document
    filename = "Nord_Stern_Database_Schema.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.darkblue
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=14,
        spaceAfter=8,
        spaceBefore=12,
        textColor=colors.darkgreen
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        alignment=TA_JUSTIFY
    )
    
    # Build the story (content)
    story = []
    
    # Title page
    story.append(Paragraph("Nord Stern Car Numbers", title_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph("Database Schema Documentation", heading_style))
    story.append(Spacer(1, 30))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", normal_style))
    story.append(Spacer(1, 40))
    story.append(Paragraph("Drivers Education Car Number Management System", normal_style))
    story.append(PageBreak())
    
    # Table of Contents
    story.append(Paragraph("Table of Contents", heading_style))
    story.append(Spacer(1, 20))
    
    toc_items = [
        "1. Database Overview",
        "2. Entity-Relationship Diagram", 
        "3. Table Structure",
        "4. Field Descriptions",
        "5. Constraints and Rules",
        "6. Business Logic",
        "7. Sample Data",
        "8. Database File Information"
    ]
    
    for item in toc_items:
        story.append(Paragraph(f"• {item}", normal_style))
    
    story.append(PageBreak())
    
    # 1. Database Overview
    story.append(Paragraph("1. Database Overview", heading_style))
    story.append(Paragraph(
        "The Nord Stern Car Numbers system uses a single-table SQLite database to manage car number registrations "
        "for Drivers Education sessions. The database is designed for simplicity, reliability, and ease of maintenance.",
        normal_style
    ))
    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "Key Features:",
        subheading_style
    ))
    story.append(Paragraph("• Single table design for maximum simplicity", normal_style))
    story.append(Paragraph("• SQLite database for portability and reliability", normal_style))
    story.append(Paragraph("• Automatic timestamp management", normal_style))
    story.append(Paragraph("• Unique car number enforcement", normal_style))
    story.append(Paragraph("• Flexible status tracking", normal_style))
    story.append(PageBreak())
    
    # 2. Entity-Relationship Diagram
    story.append(Paragraph("2. Entity-Relationship Diagram", heading_style))
    story.append(Paragraph(
        "The system uses a single entity: CAR_REGISTRATIONS. This table contains all information "
        "related to car number registrations, driver details, and vehicle information.",
        normal_style
    ))
    story.append(Spacer(1, 20))
    
    # Create ER diagram table
    er_data = [
        ['Field Name', 'Data Type', 'Constraints', 'Description'],
        ['id', 'INTEGER', 'PRIMARY KEY, AUTOINCREMENT', 'Unique identifier'],
        ['first_name', 'TEXT', 'NOT NULL', 'Driver first name'],
        ['last_name', 'TEXT', 'NOT NULL', 'Driver last name'],
        ['car_number', 'TEXT', 'UNIQUE, NOT NULL', 'Car number (formatted)'],
        ['car_make', 'TEXT', 'NULL', 'Vehicle manufacturer'],
        ['car_model', 'TEXT', 'NULL', 'Vehicle model'],
        ['car_year', 'INTEGER', 'NULL', 'Vehicle year'],
        ['car_color', 'TEXT', 'NULL', 'Vehicle color'],
        ['reserved_date', 'DATE', 'NULL', 'Reservation date'],
        ['reserved_for_year', 'INTEGER', 'DEFAULT 2025', 'Year of reservation'],
        ['status', 'TEXT', 'DEFAULT "Active"', 'Registration status'],
        ['notes', 'TEXT', 'NULL', 'Additional notes'],
        ['created_at', 'TIMESTAMP', 'DEFAULT CURRENT_TIMESTAMP', 'Creation timestamp'],
        ['updated_at', 'TIMESTAMP', 'DEFAULT CURRENT_TIMESTAMP', 'Last update timestamp']
    ]
    
    er_table = Table(er_data, colWidths=[1.5*inch, 1*inch, 1.5*inch, 2*inch])
    er_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    
    story.append(er_table)
    story.append(PageBreak())
    
    # 3. Table Structure
    story.append(Paragraph("3. Table Structure", heading_style))
    story.append(Paragraph(
        "The car_registrations table is the core of the system, containing all registration data "
        "in a normalized structure that supports efficient querying and data integrity.",
        normal_style
    ))
    story.append(Spacer(1, 20))
    
    # SQL CREATE statement
    sql_create = """
    CREATE TABLE car_registrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        car_number TEXT UNIQUE NOT NULL,
        car_make TEXT,
        car_model TEXT,
        car_year INTEGER,
        car_color TEXT,
        reserved_date DATE,
        reserved_for_year INTEGER DEFAULT 2025,
        status TEXT DEFAULT 'Active',
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    story.append(Paragraph("SQL CREATE Statement:", subheading_style))
    story.append(Paragraph(f"<code>{sql_create}</code>", normal_style))
    story.append(PageBreak())
    
    # 4. Field Descriptions
    story.append(Paragraph("4. Field Descriptions", heading_style))
    
    field_descriptions = [
        ["Primary Key", "id", "Auto-incrementing unique identifier for each registration"],
        ["Required Fields", "first_name", "Driver's first name - must be provided"],
        ["", "last_name", "Driver's last name - must be provided"],
        ["", "car_number", "Car number - must be unique and provided"],
        ["Optional Fields", "car_make", "Vehicle manufacturer (e.g., BMW, Porsche, Audi)"],
        ["", "car_model", "Vehicle model (e.g., M3, 911, RS4)"],
        ["", "car_year", "Manufacturing year of the vehicle"],
        ["", "car_color", "Color of the vehicle"],
        ["", "reserved_date", "Date when the car number was reserved"],
        ["", "notes", "Additional information or special notes"],
        ["Auto-Managed", "reserved_for_year", "Defaults to 2025, can be modified"],
        ["", "status", "Defaults to 'Active', tracks registration status"],
        ["", "created_at", "Automatically set when record is created"],
        ["", "updated_at", "Automatically updated when record is modified"]
    ]
    
    field_table = Table(field_descriptions, colWidths=[1.2*inch, 1.5*inch, 3.3*inch])
    field_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    
    story.append(field_table)
    story.append(PageBreak())
    
    # 5. Constraints and Rules
    story.append(Paragraph("5. Constraints and Rules", heading_style))
    
    constraints = [
        ["Constraint Type", "Field", "Rule", "Impact"],
        ["Primary Key", "id", "Auto-incrementing unique identifier", "Ensures each record is unique"],
        ["Unique", "car_number", "No duplicate car numbers allowed", "Prevents conflicts in car number assignments"],
        ["Not Null", "first_name", "Must have a value", "Ensures driver identification"],
        ["Not Null", "last_name", "Must have a value", "Ensures driver identification"],
        ["Not Null", "car_number", "Must have a value", "Ensures car number assignment"],
        ["Default", "reserved_for_year", "Defaults to 2025", "Sets current year automatically"],
        ["Default", "status", "Defaults to 'Active'", "Sets initial status automatically"],
        ["Auto", "created_at", "Set on record creation", "Tracks when record was created"],
        ["Auto", "updated_at", "Updated on record modification", "Tracks last modification time"]
    ]
    
    constraint_table = Table(constraints, colWidths=[1.2*inch, 1.2*inch, 2*inch, 1.6*inch])
    constraint_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    
    story.append(constraint_table)
    story.append(PageBreak())
    
    # 6. Business Logic
    story.append(Paragraph("6. Business Logic", heading_style))
    
    story.append(Paragraph("Car Number Management:", subheading_style))
    story.append(Paragraph("• Car numbers are stored as TEXT with leading zeros (e.g., '001', '014', '123')", normal_style))
    story.append(Paragraph("• Numbers are automatically formatted to 3 digits with leading zeros", normal_style))
    story.append(Paragraph("• Must be unique across all registrations", normal_style))
    story.append(Paragraph("• Supports both positive and negative numbers", normal_style))
    
    story.append(Spacer(1, 12))
    story.append(Paragraph("Status Values:", subheading_style))
    story.append(Paragraph("• Active: Currently registered and participating", normal_style))
    story.append(Paragraph("• Retired: No longer active but record preserved", normal_style))
    story.append(Paragraph("• Pending: Registration in progress", normal_style))
    
    story.append(Spacer(1, 12))
    story.append(Paragraph("Timestamp Management:", subheading_style))
    story.append(Paragraph("• created_at: Set once when record is created", normal_style))
    story.append(Paragraph("• updated_at: Updated every time record is modified", normal_style))
    story.append(Paragraph("• Both use SQLite's CURRENT_TIMESTAMP function", normal_style))
    
    story.append(PageBreak())
    
    # 7. Sample Data
    story.append(Paragraph("7. Sample Data", heading_style))
    
    sample_data = [
        ['ID', 'First Name', 'Last Name', 'Car #', 'Make', 'Model', 'Year', 'Color', 'Status'],
        ['1', 'John', 'Doe', '001', 'BMW', 'M3', '2020', 'Black', 'Active'],
        ['2', 'Jane', 'Smith', '002', 'Porsche', '911', '2021', 'Red', 'Active'],
        ['3', 'Bob', 'Johnson', '014', 'Audi', 'RS4', '2019', 'Silver', 'Retired'],
        ['4', 'Alice', 'Brown', '123', 'Mercedes', 'AMG', '2022', 'White', 'Active'],
        ['5', 'Charlie', 'Wilson', '999', 'Ferrari', 'F8', '2023', 'Yellow', 'Pending']
    ]
    
    sample_table = Table(sample_data, colWidths=[0.4*inch, 0.8*inch, 0.8*inch, 0.5*inch, 0.8*inch, 0.8*inch, 0.5*inch, 0.6*inch, 0.6*inch])
    sample_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    
    story.append(sample_table)
    story.append(PageBreak())
    
    # 8. Database File Information
    story.append(Paragraph("8. Database File Information", heading_style))
    
    file_info = [
        ["Property", "Value", "Description"],
        ["File Name", "car_numbers.db", "Main database file"],
        ["Database Type", "SQLite 3.x", "Lightweight, file-based database"],
        ["Location", "Application root", "Same directory as app.py"],
        ["File Size", "Variable", "Grows with data volume"],
        ["Backup", "Recommended", "Before major operations"],
        ["Portability", "High", "Single file, easy to move/copy"],
        ["Concurrency", "Limited", "Single writer, multiple readers"],
        ["Performance", "Excellent", "For small to medium datasets"]
    ]
    
    file_table = Table(file_info, colWidths=[1.5*inch, 1.5*inch, 2*inch])
    file_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    
    story.append(file_table)
    
    # Build the PDF
    doc.build(story)
    
    print(f"✅ PDF generated successfully: {filename}")
    print(f"📁 Location: {os.path.abspath(filename)}")
    
    return filename

if __name__ == "__main__":
    try:
        # Check if reportlab is available
        import reportlab
        create_schema_pdf()
    except ImportError:
        print("❌ Error: reportlab library not found.")
        print("📦 Install it with: pip install reportlab")
        print("💡 Alternative: Use the existing database_schema.txt file") 