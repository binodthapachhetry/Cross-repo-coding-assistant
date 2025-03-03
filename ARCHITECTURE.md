# Aider Cross-Repository Architecture

This document describes the architecture of the Aider Cross-Repository system, which enables working with multiple codebases simultaneously.

## System Design

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       Cross-Repository Assistant                         │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           Repository Manager                             │
│                                                                          │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────┐  │
│  │   Repository 1  │    │   Repository 2  │    │   Repository N      │  │
│  │   (GitRepo)     │◄──►│   (GitRepo)     │◄──►│   (GitRepo)         │  │
│  └─────────────────┘    └─────────────────┘    └─────────────────────┘  │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         Multi-Repo Indexer                               │
│                                                                          │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────┐  │
│  │  Repo 1 Index   │    │  Repo 2 Index   │    │  Repo N Index       │  │
│  │  (RepoMap)      │    │  (RepoMap)      │    │  (RepoMap)          │  │
│  └─────────────────┘    └─────────────────┘    └─────────────────────┘  │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                    Cross-Repo Dependency Graph                       │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       Cross-Repo Context Manager                         │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                    Unified Context Window                            │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                    Source Mapping Registry                           │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Integration Analyzer                              │
│                                                                          │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────┐  │
│  │ Semantic        │    │ API             │    │ Dependency          │  │
│  │ Similarity      │    │ Compatibility   │    │ Validation          │  │
│  └─────────────────┘    └─────────────────┘    └─────────────────────┘  │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       Code Adaptation Engine                             │
│                                                                          │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────┐  │
│  │ Namespace       │    │ Type            │    │ Dependency          │  │
│  │ Resolution      │    │ Compatibility   │    │ Resolution          │  │
│  └─────────────────┘    └─────────────────┘    └─────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. Repository Manager

**Purpose**: Manage multiple Git repositories simultaneously.

**Key Data Structures**:
```python
class RepositoryManager:
    repositories: Dict[str, GitRepo]  # Map of repo names to GitRepo instances
    active_repos: List[str]  # Currently active repositories
    
    def add_repository(self, name: str, path: str) -> GitRepo:
        # Add a new repository to the manager
        
    def get_repository(self, name: str) -> GitRepo:
        # Get a repository by name
        
    def resolve_path(self, repo_prefixed_path: str) -> Tuple[GitRepo, str]:
        # Resolve a repo-prefixed path (e.g., "repo1/path/to/file.py")
        # to a (repo, relative_path) tuple
```

### 2. Multi-Repo Indexer

**Purpose**: Create and maintain searchable indexes for multiple repositories.

**Key Data Structures**:
```python
class MultiRepoIndexer:
    repo_maps: Dict[str, RepoMap]  # Map of repo names to RepoMap instances
    dependency_graph: CrossRepoGraph  # Graph of dependencies between repositories
    
    def index_repository(self, repo: GitRepo) -> RepoMap:
        # Create or update the index for a repository
        
    def search_across_repos(self, query: str, limit: int = 10) -> List[SearchResult]:
        # Search across all indexed repositories
        
    def find_related_files(self, file_path: str, repo_name: str) -> List[RelatedFile]:
        # Find files related to a given file across all repositories
```

### 3. Cross-Repo Context Manager

**Purpose**: Manage context windows that span multiple repositories.

**Key Data Structures**:
```python
class CrossRepoContext:
    context_items: List[ContextItem]  # Items in the current context
    source_mapping: Dict[str, SourceLocation]  # Map of context items to source locations
    token_budget: int  # Available tokens for context
    
    def add_to_context(self, repo: str, file_path: str, priority: int = 0) -> bool:
        # Add a file to the context with priority
        
    def optimize_context(self, query: str) -> None:
        # Optimize the context based on the current query
        
    def get_unified_context(self) -> str:
        # Get the unified context for the LLM
```

### 4. Integration Analyzer

**Purpose**: Analyze integration possibilities between repositories.

**Key Data Structures**:
```python
class IntegrationAnalyzer:
    semantic_index: Dict[str, List[SemanticEntity]]  # Map of repos to semantic entities
    
    def find_similar_components(self, entity: SemanticEntity) -> List[SimilarityMatch]:
        # Find semantically similar components across repositories
        
    def check_api_compatibility(self, source: APIEntity, target: APIEntity) -> CompatibilityResult:
        # Check if two APIs are compatible
        
    def validate_dependencies(self, entity: SemanticEntity, target_repo: str) -> ValidationResult:
        # Validate that dependencies can be satisfied in the target repo
```

### 5. Code Adaptation Engine

**Purpose**: Adapt code from one repository context to another.

**Key Data Structures**:
```python
class CodeAdapter:
    namespace_map: Dict[str, str]  # Map of source namespaces to target namespaces
    type_map: Dict[str, str]  # Map of source types to target types
    
    def adapt_code(self, code: str, source_repo: str, target_repo: str) -> str:
        # Adapt code from source repo to target repo
        
    def resolve_imports(self, code: str, target_repo: str) -> str:
        # Resolve imports for the target repository
        
    def detect_conflicts(self, code: str, target_repo: str) -> List[Conflict]:
        # Detect potential conflicts when adapting code
```

## Component Interaction Sequence

1. **Repository Selection and Indexing**:
   ```
   User -> RepositoryManager: Add repositories
   RepositoryManager -> MultiRepoIndexer: Index repositories
   MultiRepoIndexer -> CrossRepoGraph: Build dependency graph
   ```

2. **Cross-Repository Query**:
   ```
   User -> Coder: Query about cross-repo functionality
   Coder -> MultiRepoIndexer: Search across repositories
   MultiRepoIndexer -> CrossRepoContext: Populate context with relevant files
   CrossRepoContext -> Model: Provide optimized context
   ```

3. **Code Transplantation**:
   ```
   User -> Coder: Request to adapt code from Repo A to Repo B
   Coder -> IntegrationAnalyzer: Analyze compatibility
   IntegrationAnalyzer -> CodeAdapter: Request code adaptation
   CodeAdapter -> Coder: Return adapted code
   Coder -> RepositoryManager: Apply changes to target repository
   ```

## Risk Analysis

1. **Context Window Limitations**:
   - **Risk**: Multiple repositories could easily exceed context window limits.
   - **Mitigation**: Implement intelligent context pruning and chunking strategies.

2. **Namespace Conflicts**:
   - **Risk**: Similar naming conventions across repositories could cause confusion.
   - **Mitigation**: Implement explicit repository prefixing and namespace isolation.

3. **Dependency Resolution**:
   - **Risk**: Dependencies may not be satisfiable across repositories.
   - **Mitigation**: Build comprehensive dependency graphs and validation checks.

4. **Performance Degradation**:
   - **Risk**: Indexing multiple large repositories could impact performance.
   - **Mitigation**: Implement incremental indexing and caching strategies.

5. **Incorrect Code Adaptation**:
   - **Risk**: Automated code adaptation might introduce subtle bugs.
   - **Mitigation**: Implement validation tests and human review prompts.

## Development Roadmap

### Phase 1: Minimum Multi-Repo Viability

1. Extend `GitRepo` to support multiple repositories
2. Create `RepositoryManager` to manage multiple repositories
3. Extend `RepoMap` to support multiple repositories
4. Implement basic cross-repository file referencing
5. Update UI/UX to support multiple repositories

### Phase 2: Integration Analysis Foundations

1. Implement `CrossRepoGraph` for dependency tracking
2. Develop semantic similarity detection
3. Create API compatibility checking
4. Build dependency validation system
5. Implement basic integration suggestions

### Phase 3: Production-Ready Code Transplantation

1. Develop the `CodeAdapter` for cross-repo code adaptation
2. Implement namespace resolution strategies
3. Create type compatibility transformations
4. Build dependency resolution mechanisms
5. Develop conflict detection and resolution workflows

### Phase 4: Performance Optimizations

1. Implement incremental indexing for large codebases
2. Optimize vector search across repositories
3. Develop advanced context window budgeting
4. Implement caching for frequent cross-repo patterns
5. Add performance monitoring and analytics

## Validation Strategy

1. **Test Repository Suite**:
   - Create a set of test repositories with known integration points
   - Include repositories with different languages and frameworks
   - Design repositories with intentional compatibility challenges

2. **Integration Test Cases**:
   - Define specific cross-repository integration scenarios
   - Create benchmark tasks for code transplantation
   - Develop metrics for measuring adaptation accuracy

3. **Performance Benchmarks**:
   - Measure indexing performance across repository sizes
   - Benchmark context window optimization strategies
   - Test search performance across multiple repositories

4. **User Experience Testing**:
   - Develop user scenarios for cross-repository tasks
   - Measure time-to-completion for integration tasks
   - Gather feedback on UI/UX for multi-repository support
