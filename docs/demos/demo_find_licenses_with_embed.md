# 🔍 Multi-Model Find Licenses Demo with Embed

## 📋 **Tool Overview**
The `find_licenses` tool now supports **relationship-aware queries** using the `embed` parameter for lazy-loading related entities.

## 🎯 **Available Embed Options**
- `license_owners` - Embed related license owner information

## 💡 **Example Usage**

### **Example 1: Basic License Search (No Embedding)**
```json
{
  "EmirateNameEn": "Dubai",
  "BlStatusEn": "Current",
  "limit": 5
}
```

**Result**: Returns license records only
```json
[
  {
    "license_pk": "4c1365eb25f87ae0e7...",
    "bl": "662456",
    "bl_name_en": "A R N TECHNICAL SERVICES",
    "emirate_name_en": "Dubai",
    "bl_status_en": "Current"
  }
]
```

### **Example 2: License Search WITH Embedded Owners (Multi-Model)**
```json
{
  "EmirateNameEn": "Dubai",
  "BlStatusEn": "Current", 
  "embed": ["license_owners"],
  "limit": 5
}
```

**Result**: Returns license records WITH embedded owner data
```json
[
  {
    "license_pk": "4c1365eb25f87ae0e7...",
    "bl": "662456",
    "bl_name_en": "A R N TECHNICAL SERVICES",
    "emirate_name_en": "Dubai",
    "bl_status_en": "Current",
    "_embedded": {
      "total_owners": 1,
      "owners": [
        {
          "owner_name": "Ahmed Al Mansoori",
          "owner_type": "Primary",
          "ownership_percentage": 100.0,
          "is_primary_owner": true
        }
      ]
    }
  }
]
```

## 🚀 **Advanced Examples**

### **Example 3: Find Licenses by Business Type with Owners**
```json
{
  "BlTypeEn": "Commercial",
  "BlEstDateFrom": "2020-01-01",
  "embed": ["license_owners"],
  "limit": 10
}
```

### **Example 4: Geographic Search with Ownership Details**
```json
{
  "EmirateNameEn": "Abu Dhabi",
  "LatDdMin": 24.0,
  "LatDdMax": 25.0,
  "embed": ["license_owners"],
  "limit": 20
}
```

## ⚡ **Performance Benefits**

### **Without Embed (Traditional)**
- ✅ Fast license query
- ❌ Need separate query for owners
- ❌ Manual data joining required

### **With Embed (Multi-Model)**
- ✅ Single query gets everything
- ✅ Automatic relationship handling  
- ✅ Lazy loading (only when requested)
- ✅ Structured JSON response

## 🎛️ **LLM Autocompletion Support**

The `embed` parameter provides intelligent autocompletion:
- **Enum values**: `["license_owners"]`
- **Type safety**: Array of strings
- **Discovery**: LLMs can suggest available relationships
- **Validation**: Clear error messages for invalid values

## 🔧 **How It Works**

1. **Base Query**: Filters licenses based on your criteria
2. **Relationship Detection**: Automatically detects related license_owners
3. **Conditional Embedding**: Only fetches related data when `embed` is specified
4. **JSON Aggregation**: Structures related data in `_embedded` field
5. **Performance Optimization**: Uses efficient JOINs and aggregation

## 📊 **Use Cases**

- **Business Analysis**: "Find all Dubai restaurants and their owners"
- **Compliance Checking**: "Get licenses expiring soon with ownership details"
- **Geographic Analysis**: "Map businesses in specific areas with owner info"
- **Relationship Mapping**: "Analyze ownership patterns across emirates"

## 🎯 **Next Steps**

Try the tool with different combinations:
- Filter by emirate + embed owners
- Search by business activity + embed owners  
- Date range queries + embed owners
- Geographic bounds + embed owners

**The multi-model framework makes complex business queries simple and efficient!** 🚀 