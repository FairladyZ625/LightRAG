# YG System Documentation (Version 1.1)

## Entity Documentation - Complete Reference

This document provides comprehensive documentation for all entities in the YG system. Each entity is documented with full details including all fields, annotations, relationships, and business methods.

---

## Base Classes

### BaseEntity
**Package:** `org.mda.yg.common.base`
**Description:** Abstract base entity providing common audit fields and soft delete functionality.

**Annotations:**
- `@Data` - Lombok annotation for getters, setters, equals, hashCode, toString
- Implements `Serializable`

**Fields:**
- `createTime: LocalDateTime` - Creation timestamp
  - `@JsonInclude(value = JsonInclude.Include.NON_NULL)`
  - `@JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")`
- `updateTime: LocalDateTime` - Last update timestamp
  - `@JsonInclude(value = JsonInclude.Include.NON_NULL)`
  - `@JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")`
- `createBy: Long` - Creator user ID
- `updateBy: Long` - Last updater user ID
- `deleted: Boolean` - Soft delete flag

**Abstract Methods:**
- `getId(): String` - Must be implemented by subclasses to provide entity ID

### Node
**Package:** `org.mda.yg.model.entity`
**Description:** Abstract base class for tree-structured entities, extends BaseEntity.

**Annotations:**
- `@Getter` - Lombok getter methods
- `@Setter` - Lombok setter methods

**Fields:**
- `fileId: String` - Associated file/project ID
- `parentId: String` - Parent node ID for tree structure
- `name: String` - Node name/title

---

## Core Entities

### 1. AnalysisDiagram
**Package:** `org.mda.yg.model.entity`
**Collection:** `analysis_diagram`
**Description:** Analysis diagram entity for project analysis visualization.

**Inheritance:** Extends `Node` (which extends `BaseEntity`)

**Annotations:**
- `@EqualsAndHashCode(callSuper = true)`
- `@Data`
- `@Document(collection = "analysis_diagram")`

**Fields:**
- `id: String` - Primary key with `@Id` annotation

### 2. CommitLog
**Package:** `org.mda.yg.model.entity`
**Collection:** `commit_log`
**Description:** Comprehensive audit log for tracking all system operations and changes.

**Annotations:**
- `@Data`
- `@Document("commit_log")`
- Implements `Serializable`

**Fields:**
- `id: String` - Primary key with `@Id` annotation
- `operation: OperationEnum` - Type of operation performed
- `targetObject: Map<String, Object>` - Target object being operated on
- `newObject: Map<String, Object>` - New/changed data
- `requestUri: String` - HTTP request URI
- `ip: String` - Client IP address
- `province: String` - Client's province
- `city: String` - Client's city
- `browser: String` - Client browser
- `browserVersion: String` - Browser version
- `os: String` - Operating system
- `executionTime: Long` - Execution time in milliseconds
- `createBy: Long` - Creator user ID
- `createByName: String` - Creator user name
- `createTime: LocalDateTime` - Creation timestamp

### 3. Dir
**Package:** `org.mda.yg.model.entity`
**Collection:** `dir`
**Description:** Directory/folder entity for organizing project structure.

**Inheritance:** Extends `Node` (which extends `BaseEntity`)

**Annotations:**
- `@EqualsAndHashCode(callSuper = true)`
- `@Data`
- `@Document(collection = "dir")`

**Fields:**
- `id: String` - Primary key with `@Id` annotation

### 4. File
**Package:** `org.mda.yg.model.entity`
**Collection:** `file`
**Description:** Main project file entity representing a complete project/document.

**Inheritance:** Extends `BaseEntity`

**Annotations:**
- `@EqualsAndHashCode(callSuper = true)`
- `@Data`
- `@Document(collection = "file")`

**Fields:**
- `id: String` - Primary key with `@Id` annotation
- `name: String` - Project/file name
- `description: String` - Project description
- `author: String` - Project author
- `requirementsQuantity: Integer` - Number of requirements (default: 0)
- `collect: Boolean` - Favorite flag (default: false)
- `templateId: String` - Associated template ID
- `preferredRequirementKind: String` - Preferred requirement type
- `cloneRequirements: List<String>` - List of cloneable requirement IDs
- `lifecycleId: String` - Associated lifecycle ID
- `openTime: LocalDateTime` - Last opened timestamp
- `cloudProjectId: Long` - Cloud project ID
- `cloudFileId: Long` - Cloud file ID

### 5. FileLifeCycle
**Package:** `org.mda.yg.model.entity`
**Collection:** `file_life_cycle`
**Description:** Project-specific lifecycle configuration.

**Inheritance:** Extends `BaseEntity`

**Annotations:**
- `@Data`
- `@Document("file_life_cycle")`

**Fields:**
- `id: String` - Primary key with `@MongoId` annotation
- `fileId: String` - Associated project file ID
- `name: String` - Lifecycle name
- `phases: List<Phase>` - List of lifecycle phases

### 6. FileRequirementField
**Package:** `org.mda.yg.model.entity`
**Collection:** `file_requirement_field`
**Description:** Project-specific requirement field configuration.

**Inheritance:** Extends `BaseEntity`

**Annotations:**
- `@Data`
- `@Builder`
- `@AllArgsConstructor`
- `@NoArgsConstructor`
- `@Document(collection = "file_requirement_field")`

**Fields:**
- `id: String` - Primary key with `@Id` annotation
- `fileId: String` - Associated project file ID
- `name: String` - Field name
- `componentType: ComponentType` - UI component type
- `description: String` - Field description
- `componentContent: String` - Component configuration/content
- `required: Boolean` - Required flag
- `sourceType: SourceType` - Source type enumeration

### 7. FileRequirementKind
**Package:** `org.mda.yg.model.entity`
**Collection:** `file_requirement_kind`
**Description:** Project-specific requirement type configuration.

**Inheritance:** Extends `BaseEntity`

**Annotations:**
- `@Data`
- `@Builder`
- `@AllArgsConstructor`
- `@NoArgsConstructor`
- `@Document(collection = "file_requirement_kind")`

**Fields:**
- `id: String` - Primary key with `@Id` annotation
- `fileId: String` - Associated project file ID
- `name: String` - Requirement type name
- `fieldIds: List<String>` - Associated field IDs
- `sourceType: SourceType` - Source type enumeration

### 8. FileTemplate
**Package:** `org.mda.yg.model.entity`
**Collection:** `file_template`
**Description:** Template entity for project templates.

**Inheritance:** Extends `BaseEntity`

**Annotations:**
- `@Data`
- `@Document("file_template")`

**Fields:**
- `id: String` - Primary key with `@MongoId` annotation
- `name: String` - Template name
- `type: Integer` - Template type (0: system template, 1: custom template)
- `lifeCycleId: String` - Associated lifecycle ID
- `requirementKindIds: List<String>` - Requirement type IDs
- `firstRequirementKindId: String` - Primary requirement type ID
- `desc: String` - Template description

### 9. LifeCycle
**Package:** `org.mda.yg.model.entity`
**Collection:** `life_cycle`
**Description:** System-level lifecycle template.

**Inheritance:** Extends `BaseEntity`

**Annotations:**
- `@Data`
- `@Document("life_cycle")`

**Fields:**
- `id: String` - Primary key with `@MongoId` annotation
- `name: String` - Lifecycle name
- `phases: List<Phase>` - List of lifecycle phases

### 10. Matrix
**Package:** `org.mda.yg.model.entity`
**Collection:** `matrix`
**Description:** Matrix entity for requirement relationship matrices.

**Inheritance:** Extends `Node` (which extends `BaseEntity`)

**Annotations:**
- `@EqualsAndHashCode(callSuper = true)`
- `@Data`
- `@Document(collection = "matrix")`

**Fields:**
- `id: String` - Primary key with `@Id` annotation
- `rowScope: List<String>` - Row scope identifiers
- `columnScope: List<String>` - Column scope identifiers
- `relationshipTypes: List<RelationshipTypeEnum>` - Relationship types
- `relationshipDirection: RelationshipDirectionEnum` - Relationship direction

### 11. Node (Abstract)
**Package:** `org.mda.yg.model.entity`
**Description:** Abstract base class for tree-structured entities.

**Annotations:**
- `@Getter` - Lombok getter methods
- `@Setter` - Lombok setter methods

**Fields:**
- `fileId: String` - Associated file/project ID
- `parentId: String` - Parent node ID for hierarchical structure
- `name: String` - Node name/title

### 12. OperationLog
**Package:** `org.mda.yg.model.entity`
**Collection:** `operation_log`
**Description:** Operation log for tracking user operations within projects.

**Annotations:**
- `@Data`
- `@Document("operation_log")`

**Fields:**
- `id: String` - Primary key with `@Id` annotation
- `fileId: String` - Associated project file ID
- `operationModuleEnum: OperationModuleEnum` - Operation module/category
- `operationTypeEnum: OperationTypeEnum` - Operation type
- `operationInfoDisplay: String` - Human-readable operation description
- `objectIds: List<String>` - IDs of affected objects
- `objectNames: List<String>` - Names of affected objects
- `objectInfoDisplays: List<String>` - Display information for affected objects
- `extend: Map<Object, Object>` - Additional extension data
- `createBy: Long` - Creator user ID
- `createByName: String` - Creator user name
- `createTime: LocalDateTime` - Creation timestamp with MongoDB index for sorting

### 13. Phase
**Package:** `org.mda.yg.model.entity`
**Description:** Lifecycle phase configuration.

**Annotations:**
- `@Data`

**Fields:**
- `id: String` - Phase identifier
- `name: String` - Phase name
- `backColor: String` - Background color for UI display

### 14. Relationship
**Package:** `org.mda.yg.model.entity`
**Collection:** `relationship`
**Description:** Entity representing relationships between requirements.

**Inheritance:** Extends `BaseEntity`

**Annotations:**
- `@Getter`
- `@Setter`
- `@Document(collection = "relationship")`

**Fields:**
- `id: String` - Primary key with `@Id` annotation
- `fileId: String` - Associated project file ID
- `type: RelationshipTypeEnum` - Relationship type
- `sourceId: String` - Source requirement ID
- `targetId: String` - Target requirement ID

**Methods:**
- `getId(): String` - Returns the relationship ID

### 15. Requirement
**Package:** `org.mda.yg.model.entity`
**Collection:** `requirements`
**Description:** Main requirement entity using flexible key-value structure.

**Inheritance:** Extends `HashMap<String, Object>`

**Annotations:**
- `@Data`
- `@Document(collection = "requirements")`

**Static Fields:**
- `DATETIME_FORMATTER: DateTimeFormatter` - Date format pattern "yyyy-MM-dd HH:mm:ss"
- `fileFieldNameMap: Map<String, String>` - Transient field name mapping

**Constructors:**
- `Requirement(String parentId, String fileId, String tableId, Map<String, String> fileFieldNameMap)` - Constructor with initialization
- `Requirement()` - Default constructor

**Key Methods:**
- `getId(): String` - Returns requirement ID from "_id"
- `getNormalId(): String` - Returns requirement ID from "id"
- `getTableId(): String` - Returns table ID
- `getFieldValue(String fieldId): String` - Gets field value as string
- `setFieldValue(String fieldId, String value)` - Sets field value with null handling
- `getBooleanValue(String fieldId): Boolean` - Gets boolean field value
- `getNumberValue(String fieldId): Double` - Gets numeric field value
- `getDeleted(): Boolean` - Gets deleted flag
- `getParentId(): String` - Gets parent requirement ID
- `getTitle(): String` - Gets title field (dynamically resolved)
- `getContent(): String` - Gets content field (dynamically resolved)
- `getSerialNumber(): String` - Gets serial number field (dynamically resolved)
- `getTimeTypeData(String key): LocalDateTime` - Specialized date parsing with multiple format support
- `removeAll(List<String> fieldsToDelete)` - Removes multiple fields

**Built-in Fields:**
- `创建人员` - Creator (initialized to current user)
- `更新人员` - Updater (initialized to current user)
- `创建时间` - Creation time (initialized to now)
- `更新时间` - Update time (initialized to now)
- `parentId` - Parent requirement ID (default: "-1")
- `deleted` - Soft delete flag (default: false)
- `fileId` - Associated project file ID
- `tableId` - Associated table ID

### 16. RequirementField
**Package:** `org.mda.yg.model.entity`
**Collection:** `requirement_field`
**Description:** System-level requirement field template configuration.

**Inheritance:** Extends `BaseEntity`

**Annotations:**
- `@Data`
- `@Builder`
- `@AllArgsConstructor`
- `@NoArgsConstructor`
- `@Document(collection = "requirement_field")`

**Fields:**
- `id: String` - Primary key with `@Id` annotation
- `name: String` - Field name
- `componentType: ComponentType` - UI component type
- `description: String` - Field description
- `componentContent: String` - Component configuration/content
- `required: Boolean` - Required flag
- `sourceType: SourceType` - Source type enumeration

### 17. RequirementKind
**Package:** `org.mda.yg.model.entity`
**Collection:** `requirement_kind`
**Description:** System-level requirement type/category configuration.

**Inheritance:** Extends `BaseEntity`

**Annotations:**
- `@Data`
- `@Builder`
- `@AllArgsConstructor`
- `@NoArgsConstructor`
- `@Document(collection = "requirement_kind")`

**Fields:**
- `id: String` - Primary key with `@Id` annotation
- `name: String` - Requirement type name
- `fieldIds: List<String>` - Associated field IDs
- `sourceType: SourceType` - Source type enumeration

### 18. SysLog
**Package:** `org.mda.yg.model.entity`
**Collection:** `sys_log`
**Description:** System-level logging for application events.

**Annotations:**
- `@Data`
- `@Document("sys_log")`
- Implements `Serializable`

**Fields:**
- `id: ObjectId` - Primary key with `@Id` annotation (MongoDB ObjectId)
- `module: LogModuleEnum` - Log module/category
- `content: String` - Log content/message
- `requestUri: String` - HTTP request URI
- `ip: String` - Client IP address
- `province: String` - Client's province
- `city: String` - Client's city
- `browser: String` - Client browser
- `browserVersion: String` - Browser version
- `os: String` - Operating system
- `executionTime: Long` - Execution time in milliseconds
- `createBy: Long` - Creator user ID
- `createTime: LocalDateTime` - Creation timestamp

### 19. Table
**Package:** `org.mda.yg.model.entity`
**Collection:** `table`
**Description:** Requirement table entity for organizing and displaying requirements.

**Inheritance:** Extends `Node` (which extends `BaseEntity`)

**Annotations:**
- `@EqualsAndHashCode(callSuper = true)`
- `@Data`
- `@Document(collection = "table")`

**Fields:**
- `id: String` - Primary key with `@Id` annotation
- `displayed: LinkedHashSet<String>` - Display field configuration
- `tableHeadOrdered: LinkedHashMap<String, String>` - Ordered table header mapping

### 20. TraceDiagram
**Package:** `org.mda.yg.model.entity`
**Collection:** `trace_diagram`
**Description:** Traceability diagram entity for requirement relationship analysis.

**Inheritance:** Extends `Node` (which extends `BaseEntity`)

**Annotations:**
- `@EqualsAndHashCode(callSuper = true)`
- `@Data`
- `@Document(collection = "trace_diagram")`

**Fields:**
- `id: String` - Primary key with `@Id` annotation
- `startId: String` - Starting requirement ID for traceability
- `relationshipTypes: List<RelationshipTypeEnum>` - Relationship types to include
- `relationshipDirection: RelationshipDirectionEnum` - Relationship direction
- `scopeId: String` - Scope ID (requirement table, folder, or project)
- `scopeType: NodeTypeEnum` - Scope type enumeration
- `displayLevel: Integer` - Display depth level
- `displayLegend: Boolean` - Legend display flag

### 21. TranctionLog
**Package:** `org.mda.yg.model.entity`
**Collection:** `tranction_log`
**Description:** Transaction log placeholder entity.

**Annotations:**
- `@Data`
- `@Document("tranction_log")`

**Fields:**
- `id: String` - Primary key with `@Id` annotation

---

## Entity Relationships Summary

### Inheritance Hierarchy
```
BaseEntity (abstract)
├── File
├── FileLifeCycle
├── FileRequirementField
├── FileRequirementKind
├── FileTemplate
├── LifeCycle
├── Relationship
├── RequirementField
├── RequirementKind
├── SysLog
└── Node (abstract)
    ├── AnalysisDiagram
    ├── Dir
    ├── Matrix
    ├── Table
    └── TraceDiagram
```

### Key Relationships
- **File** → **FileLifeCycle**: One-to-one via `lifecycleId`
- **File** → **FileTemplate**: Many-to-one via `templateId`
- **File** → **FileRequirementField**: One-to-many via `fileId`
- **File** → **FileRequirementKind**: One-to-many via `fileId`
- **Requirement** → **File**: Many-to-one via `fileId`
- **Requirement** → **Table**: Many-to-one via `tableId`
- **Relationship** → **File**: Many-to-one via `fileId`
- **Relationship** → **Requirement**: Many-to-one via `sourceId` and `targetId`
- **LifeCycle** → **Phase**: One-to-many via embedded `phases` list
- **FileLifeCycle** → **Phase**: One-to-many via embedded `phases` list
- **RequirementKind** → **RequirementField**: Many-to-many via `fieldIds`
- **FileTemplate** → **RequirementKind**: Many-to-many via `requirementKindIds`

---

## MongoDB Collections

| Entity | Collection Name | Description |
|--------|----------------|-------------|
| AnalysisDiagram | `analysis_diagram` | Analysis diagrams |
| CommitLog | `commit_log` | Comprehensive audit logs |
| Dir | `dir` | Directory/folder structure |
| File | `file` | Main project files |
| FileLifeCycle | `file_life_cycle` | Project-specific lifecycles |
| FileRequirementField | `file_requirement_field` | Project-specific fields |
| FileRequirementKind | `file_requirement_kind` | Project-specific requirement types |
| FileTemplate | `file_template` | Project templates |
| LifeCycle | `life_cycle` | System lifecycle templates |
| Matrix | `matrix` | Requirement relationship matrices |
| OperationLog | `operation_log` | User operation logs |
| Relationship | `relationship` | Requirement relationships |
| Requirement | `requirements` | Actual requirement data |
| RequirementField | `requirement_field` | System field templates |
| RequirementKind | `requirement_kind` | System requirement type templates |
| SysLog | `sys_log` | System event logs |
| Table | `table` | Requirement tables |
| TraceDiagram | `trace_diagram` | Traceability diagrams |
| TranctionLog | `tranction_log` | Transaction logs |

---

## Enumerations Used

- **OperationEnum**: Used in CommitLog for operation types
- **ComponentType**: Used in FileRequirementField and RequirementField for UI components
- **SourceType**: Used in FileRequirementField, FileRequirementKind, RequirementField, and RequirementKind
- **RelationshipTypeEnum**: Used in Matrix and Relationship for relationship types
- **RelationshipDirectionEnum**: Used in Matrix and Relationship for relationship directions
- **NodeTypeEnum**: Used in TraceDiagram for scope type
- **OperationModuleEnum**: Used in OperationLog for operation categories
- **OperationTypeEnum**: Used in OperationLog for operation types
- **LogModuleEnum**: Used in SysLog for log categories

---

## Usage Notes

1. **Soft Delete**: All entities extending BaseEntity support soft delete via the `deleted` flag
2. **Audit Fields**: All BaseEntity subclasses automatically track creation and modification metadata
3. **Flexible Requirements**: The Requirement entity uses HashMap for flexible field storage
4. **Hierarchical Structure**: Node-based entities support tree structures via parentId
5. **MongoDB Specific**: All entities use MongoDB-specific annotations for document mapping
6. **Indexes**: OperationLog has a MongoDB index on createTime for performance
7. **Validation**: Field validation is handled via ComponentType and required flags

This documentation provides a complete reference for all entities in the YG system, suitable for development, maintenance, and integration purposes.