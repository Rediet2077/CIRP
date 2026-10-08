# CIRP Admin Hierarchy Design

## Role Structure

```
                    SUPER ADMIN
                         │
        ┌────────────────┼─────────────────┐
        │                │                 │
        ▼                ▼                 ▼
   ROAD ADMIN       WATER ADMIN      ELECTRICITY ADMIN
        │                │                 │
        ▼                ▼                 ▼
 Road Service       Water Service    Electricity Service
 Centers/Areas      Centers/Areas     Centers/Areas
        │                │                 │
        ▼                ▼                 ▼
 Road Teams         Water Teams       Electrical Teams
```

## 1. SUPER ADMIN

**ONE Super Admin for the entire CIRP system**

### Responsibilities:
- ✅ Manage all departments
- ✅ Manage all service centers
- ✅ Manage geographic areas
- ✅ Manage all users (create, update, delete)
- ✅ Create and manage admin accounts
- ✅ Manage categories
- ✅ Manage department/category mapping
- ✅ Manage contractors/maintenance teams
- ✅ View and manage ALL reports (system-wide)
- ✅ System settings
- ✅ GIS management
- ✅ AI system management
- ✅ Analytics (system-wide)
- ✅ Audit logs (full access)

### Dashboard Access:
- All menu items
- All departments
- All reports
- All users
- System configuration

---

## 2. DEPARTMENT ADMINS

### 2.1 Road Admin
**Manages:** Road damage, potholes, sidewalks, road infrastructure

#### Categories Assigned:
- Road Damage
- Potholes
- Sidewalk Issues
- Road Signage

#### Responsibilities:
- ✅ View/manage reports in Road category
- ✅ Assign tasks to Road maintenance teams
- ✅ Manage Road service centers
- ✅ Track Road repair progress
- ✅ View Road analytics
- ❌ Cannot access Water, Electricity reports
- ❌ Cannot create users outside their department

---

### 2.2 Water Admin
**Manages:** Water leakage, broken pipes, water supply, sewerage

#### Categories Assigned:
- Water Leakage
- Broken Pipes
- Water Supply Issues
- Sewerage Problems

#### Responsibilities:
- ✅ View/manage reports in Water category
- ✅ Assign tasks to Water maintenance teams
- ✅ Manage Water service centers
- ✅ Track Water repair progress
- ✅ View Water analytics
- ❌ Cannot access Road, Electricity reports

---

### 2.3 Electricity Admin
**Manages:** Electrical poles, cables, transformers, electrical boxes

#### Categories Assigned:
- Damaged Electrical Poles
- Broken Cables
- Transformer Issues
- Electrical Box Problems

#### Responsibilities:
- ✅ View/manage reports in Electricity category
- ✅ Assign tasks to Electrical maintenance teams
- ✅ Manage Electricity service centers
- ✅ Track Electricity repair progress
- ✅ View Electricity analytics
- ❌ Cannot access Road, Water reports

---

### 2.4 Drainage Admin
**Manages:** Blocked drains, flooding, damaged drainage systems

#### Categories Assigned:
- Blocked Drains
- Flooding Issues
- Damaged Drainage Infrastructure

#### Responsibilities:
- ✅ View/manage reports in Drainage category
- ✅ Assign tasks to Drainage maintenance teams
- ✅ Manage Drainage service centers
- ✅ Track Drainage repair progress
- ✅ View Drainage analytics

---

### 2.5 Waste Management Admin
**Manages:** Garbage collection, illegal dumping, waste containers

#### Categories Assigned:
- Garbage Collection
- Illegal Dumping
- Damaged Waste Containers
- Overflowing Bins

#### Responsibilities:
- ✅ View/manage reports in Waste category
- ✅ Assign tasks to Waste collection teams
- ✅ Manage Waste service centers
- ✅ Track Waste collection progress
- ✅ View Waste analytics

---

### 2.6 Street Lighting Admin
**Manages:** Broken streetlights, damaged light poles

#### Categories Assigned:
- Broken Streetlights
- Damaged Light Poles
- Electrical Issues in Public Lighting

#### Responsibilities:
- ✅ View/manage reports in Street Lighting category
- ✅ Assign tasks to Street Lighting teams
- ✅ Manage Street Lighting service centers
- ✅ Track Street Lighting repair progress
- ✅ View Street Lighting analytics

---

### 2.7 Public Facilities Admin
**Manages:** Schools, public buildings, parks, public toilets

#### Categories Assigned:
- School Infrastructure Issues
- Public Building Damage
- Park Maintenance
- Public Toilet Issues
- Playground Equipment

#### Responsibilities:
- ✅ View/manage reports in Public Facilities category
- ✅ Assign tasks to Public Facilities maintenance teams
- ✅ Manage Public Facilities service centers
- ✅ Track Public Facilities repair progress
- ✅ View Public Facilities analytics

---

## Report Flow Examples

### Example 1: Water Pipe Leaking in Tafo
```
Citizen Reports Issue
   ↓
CIRP System (categorized as "Water Leakage")
   ↓
Water Admin
   ↓
Tafo Water Service Center
   ↓
Tafo Area Water Team
   ↓
Task Assigned to Plumber
```

### Example 2: Electric Pole Damaged in Summit
```
Citizen Reports Issue
   ↓
CIRP System (categorized as "Electrical Pole Damage")
   ↓
Electricity Admin
   ↓
Summit Electricity Service Center
   ↓
Summit Area Electrical Team
   ↓
Task Assigned to Electrician
```

### Example 3: Large Pothole in Arabsa
```
Citizen Reports Issue
   ↓
CIRP System (categorized as "Road Damage")
   ↓
Road Admin
   ↓
Arabsa Road Service Center
   ↓
Arabsa Area Road Team
   ↓
Task Assigned to Road Crew
```

---

## Geographic Areas (NOT Admin Roles)

**Important:** Tafo, Arabsa, Summit, etc. are **NOT admin roles**. They are **geographic areas** managed by department admins through service centers.

### Structure:
```
Department Admin
    ↓
Service Center (per area/district)
    ↓
Geographic Area (Tafo, Summit, Arabsa, etc.)
    ↓
Maintenance Teams
```

---

## Dashboard Menu Access Matrix

| Feature | Super Admin | Department Admin | Citizen |
|---------|-------------|------------------|---------|
| All Reports | ✅ | ✅ (Own dept only) | ✅ (Own only) |
| Users Management | ✅ | ❌ | ❌ |
| Departments | ✅ | ❌ | ❌ |
| Categories | ✅ | ❌ | ❌ |
| Service Centers | ✅ | ✅ (Own dept) | ❌ |
| Contractors | ✅ | ✅ (Own dept) | ❌ |
| Tasks | ✅ | ✅ (Own dept) | ❌ |
| Assets | ✅ | ✅ (Own dept) | ❌ |
| Analytics | ✅ | ✅ (Own dept) | ❌ |
| Audit Logs | ✅ | ❌ | ❌ |
| System Settings | ✅ | ❌ | ❌ |
| GIS/Map | ✅ | ✅ (Own dept) | ✅ |

---

## Implementation Checklist

### Backend
- [x] Update UserRole enum with 7 department admin roles
- [x] Update User model max_length for role field
- [x] Run migrations
- [ ] Create department-category mapping
- [ ] Update permissions middleware
- [ ] Create service center model
- [ ] Update report assignment logic

### Admin Frontend
- [ ] Update navigation based on role
- [ ] Filter reports by department
- [ ] Update users page to show role hierarchy
- [ ] Create department management page
- [ ] Create service center management
- [ ] Update analytics to filter by department
- [ ] Add role-based access control to all pages

### Mobile App
- No changes needed (citizens only see reporting interface)

---

## Next Steps

1. **Map Categories to Departments**
2. **Create Service Center Model**
3. **Update Report Assignment Flow**
4. **Implement Role-Based Navigation**
5. **Create Admin User Creation Flow**
