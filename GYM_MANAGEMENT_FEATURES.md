# Gym Management System - Core Features

This document outlines the essential features for the Gym Management System, organized by application type.

## 🏢 PARENT APP (Gym Administration)

The parent application is used by gym administrators and trainers to manage members, create training plans, and control the business.

### Essential Features (High Priority)

#### Member Management (21-25)
- **Complete member database** with personal, medical, and contact information
- **Member dashboard** showing all active members with performance indicators
- **Initial and periodic evaluations** with customizable forms
- **Routine creator** with exercise library and drag-and-drop editor
- **Program planner** with periodization and automatic intensity adjustment

#### Progress Tracking (27)
- **Individual progress reports** with automatic monthly generation
- Evolution graphs and progress photo comparisons
- Plan adherence analysis and automated recommendations

#### Communication (30)
- **Group messaging system** for announcements to all members
- Segmented messages by level, objective, etc.
- Message scheduling and read confirmation

#### Scheduling (32)
- **Schedule management** with master gym calendar
- Availability configuration
- Management of individual and group sessions

#### Business Management (35-36)
- **Membership management** with configurable types and automatic renewals
- **Payment control** with digital invoices and payment reminders
- Financial reports

#### Technical (55)
- **Advanced bidirectional synchronization** between parent and child apps
- Real-time sync with conflict resolution
- Robust offline mode

## 📱 CHILD APP (Gym Members)

The child application is used by gym members to access their training information, communicate with trainers, and track their progress.

### Essential Features (High Priority)

#### Training (1-5)
- **Real-time exercise tracking** with integrated timer and automatic weight logging
- **Exercise videos** with demonstration library
- **Interactive training plan** with calendar view and completion checkboxes
- **Body measurements recording** with weight, BMI, circumferences, and progress photos
- **Nutrition** with access to personalized meal plan and recipes

#### Statistics (7)
- **Personal dashboard** with weekly/monthly training summary
- Attendance statistics and completed objectives

#### Communication (9)
- **Enhanced messaging** with real-time chat, photo/video sending, and push notifications

#### Scheduling (12)
- **Session booking** with trainer availability calendar and automatic reminders

## 🎯 Implementation Priority

This system focuses on essential gym management functionality:
1. Member and trainer management
2. Training plan creation and assignment
3. Progress tracking and reporting
4. Communication between trainers and members
5. Schedule and session management
6. Membership and payment control

## 🔄 Architecture

- **Parent App (Madre)**: Desktop application with GUI for gym administration + REST API server
- **Child Apps (Hija)**: Desktop/mobile applications for gym members
- **Synchronization**: Real-time bidirectional sync with offline support
- **Database**: SQLite for local storage, with potential migration to PostgreSQL

---

**Focus**: Professional gym management system for exclusive gyms and their members, with emphasis on trainer-member relationship and business administration.
