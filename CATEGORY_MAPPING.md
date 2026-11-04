# CIRP Category to Department Mapping

## 📋 Category UUIDs for Mobile App

These are the **actual** category IDs from the database that must be used in the mobile app:

### 1. Road Damage → Public Works
- **Category ID**: `771ed052-e3f0-4709-bf8c-30cf532751d8`
- **Department**: Public Works
- **Examples**: Potholes, cracks, road damage, pavement issues

### 2. Water Leakage → Water & Sewage
- **Category ID**: `c0810993-eba1-4649-bab3-759c52b5b6b6`
- **Department**: Water & Sewage
- **Examples**: Pipe bursts, water leaks, supply issues

### 3. Garbage → Sanitation
- **Category ID**: `01393c0f-6bff-44ac-9533-7cdbeae21a4e`
- **Department**: Sanitation
- **Examples**: Uncollected trash, illegal dumping, waste issues

### 4. Streetlight → Electrical Services ⚡
- **Category ID**: `aeac7e07-736a-46ac-a8d4-e8d95ddc8138`
- **Department**: Electrical Services
- **Examples**: Broken lights, damaged poles, electrical issues

### 5. Drainage → Water & Sewage
- **Category ID**: `ca7060f8-52d7-478b-9a46-da95eb3ac224`
- **Department**: Water & Sewage
- **Examples**: Blocked drains, flooding, drainage issues

### 6. Other → Public Works
- **Category ID**: `0964f75b-4375-4986-803a-1a2bfaf2dd7e`
- **Department**: Public Works
- **Examples**: General infrastructure issues

---

## 🔍 Department IDs

| Department | UUID | Manager Email |
|------------|------|---------------|
| **Public Works** | `058858b2-a0f6-42c6-8afc-9839c6024c92` | public.works@cirp.com |
| **Water & Sewage** | `a96b790b-67eb-4b9d-9200-d945c33a1c8e` | water.sewage@cirp.com |
| **Sanitation** | `bb87a4ab-0ae6-4da5-b1c8-3d3168664fd2` | sanitation@cirp.com |
| **Electrical Services** | `5b97039d-a71d-41df-9cc5-c21c43d89a31` | electrical.services@cirp.com |

---

## 🔧 How Reports Are Routed

1. **Citizen submits report** from mobile app
2. **Category is selected** (e.g., "Streetlight")
3. **Backend looks up category** in database
4. **Department is automatically assigned** based on category
5. **Department head can view** their department's reports
6. **System admin can view** ALL reports

---

## ✅ Fixed Issues

### Previous Problem:
- Mobile app was using **incorrect/non-existent** category UUIDs
- Reports were being assigned to "Other" category → Public Works
- Electrical Services department couldn't see streetlight reports

### Solution:
- ✅ Updated mobile app with **correct** category UUIDs from database
- ✅ Updated existing reports to correct department
- ✅ Now Streetlight reports → Electrical Services department

---

## 📱 Mobile App Code Location

File: `mobile/lib/features/reports/screens/report_problem_screen.dart`

```dart
final categoryUUIDs = [
  '771ed052-e3f0-4709-bf8c-30cf532751d8', // Road Damage
  'c0810993-eba1-4649-bab3-759c52b5b6b6', // Water Leakage
  '01393c0f-6bff-44ac-9533-7cdbeae21a4e', // Garbage
  'aeac7e07-736a-46ac-a8d4-e8d95ddc8138', // Streetlight
  'ca7060f8-52d7-478b-9a46-da95eb3ac224', // Drainage
  '0964f75b-4375-4986-803a-1a2bfaf2dd7e', // Other
];
```

---

**Last Updated**: 2026-10-26
**Database**: cirp.db
