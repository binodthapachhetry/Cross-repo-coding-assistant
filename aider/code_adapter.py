import os
import re
from typing import Dict, List, Set, Tuple, Optional
import importlib.util
import ast

class CodeAdapter:
    """
    Adapts code from one repository context to another
    """
    
    def __init__(self, repo_manager):
        """
        Initialize the code adapter
        
        Args:
            repo_manager: RepositoryManager instance
        """
        self.repo_manager = repo_manager
        self.namespace_map = {}
        self.type_map = {}
        
    def adapt_code(self, code: str, source_repo: str, target_repo: str) -> str:
        """
        Adapt code from source repo to target repo
        
        Args:
            code: Source code to adapt
            source_repo: Name of source repository
            target_repo: Name of target repository
            
        Returns:
            Adapted code for target repository
        """
        # Get repository information
        source_repo_obj = self.repo_manager.get_repository(source_repo)
        target_repo_obj = self.repo_manager.get_repository(target_repo)
        
        if not source_repo_obj or not target_repo_obj:
            return code
            
        # Detect language
        language = self._detect_language(code)
        
        # Apply language-specific adaptations
        if language == "python":
            return self._adapt_python_code(code, source_repo, target_repo)
        elif language == "javascript" or language == "typescript":
            return self._adapt_js_code(code, source_repo, target_repo)
        else:
            # Generic adaptation for other languages
            return self._adapt_generic_code(code, source_repo, target_repo)
    
    def _detect_language(self, code: str) -> str:
        """
        Detect the programming language of the code
        
        Args:
            code: Source code
            
        Returns:
            Detected language name
        """
        # Simple heuristics for language detection
        if re.search(r'import\s+[a-zA-Z0-9_]+|from\s+[a-zA-Z0-9_.]+\s+import', code):
            return "python"
        elif re.search(r'require\(|import\s+[a-zA-Z0-9_]+\s+from|export\s+', code):
            if 'interface ' in code or 'type ' in code:
                return "typescript"
            return "javascript"
        elif re.search(r'#include|namespace\s+[a-zA-Z0-9_]+|class\s+[a-zA-Z0-9_]+\s*:', code):
            return "cpp"
        elif re.search(r'package\s+[a-zA-Z0-9_.]+;|import\s+java\.', code):
            return "java"
        else:
            return "generic"
    
    def _adapt_python_code(self, code: str, source_repo: str, target_repo: str) -> str:
        """
        Adapt Python code from source repo to target repo
        
        Args:
            code: Source Python code
            source_repo: Name of source repository
            target_repo: Name of target repository
            
        Returns:
            Adapted Python code
        """
        # Parse imports
        imports = self._extract_python_imports(code)
        
        # Build import mapping
        import_mapping = self._build_python_import_mapping(imports, source_repo, target_repo)
        
        # Replace imports
        adapted_code = code
        for old_import, new_import in import_mapping.items():
            if old_import == new_import:
                continue
            adapted_code = adapted_code.replace(old_import, new_import)
        
        # Add necessary imports
        missing_imports = self._find_missing_python_imports(adapted_code, target_repo)
        if missing_imports:
            import_block = "\n".join(missing_imports)
            # Add after existing imports or at the beginning
            if re.search(r'^import|^from', adapted_code, re.MULTILINE):
                # Find the last import statement
                last_import_match = list(re.finditer(r'^(import|from).*$', adapted_code, re.MULTILINE))[-1]
                last_import_end = last_import_match.end()
                adapted_code = adapted_code[:last_import_end] + "\n" + import_block + adapted_code[last_import_end:]
            else:
                adapted_code = import_block + "\n\n" + adapted_code
        
        return adapted_code
    
    def _extract_python_imports(self, code: str) -> List[str]:
        """
        Extract import statements from Python code
        
        Args:
            code: Python code
            
        Returns:
            List of import statements
        """
        imports = []
        for line in code.splitlines():
            if line.strip().startswith(('import ', 'from ')):
                imports.append(line.strip())
        return imports
    
    def _build_python_import_mapping(
        self, imports: List[str], source_repo: str, target_repo: str
    ) -> Dict[str, str]:
        """
        Build mapping of imports from source to target repository
        
        Args:
            imports: List of import statements
            source_repo: Name of source repository
            target_repo: Name of target repository
            
        Returns:
            Dictionary mapping source imports to target imports
        """
        mapping = {}
        source_repo_obj = self.repo_manager.get_repository(source_repo)
        target_repo_obj = self.repo_manager.get_repository(target_repo)
        
        if not source_repo_obj or not target_repo_obj:
            return mapping
            
        # Extract source repo package name (assuming it matches the repo name)
        source_package = os.path.basename(source_repo_obj.root)
        target_package = os.path.basename(target_repo_obj.root)
        
        for imp in imports:
            # Replace internal imports
            if source_package in imp:
                mapping[imp] = imp.replace(source_package, target_package)
            else:
                mapping[imp] = imp
                
        return mapping
    
    def _find_missing_python_imports(self, code: str, target_repo: str) -> List[str]:
        """
        Find imports that need to be added to the adapted code
        
        Args:
            code: Adapted Python code
            target_repo: Name of target repository
            
        Returns:
            List of import statements to add
        """
        # This would require more sophisticated analysis
        # For now, return an empty list
        return []
    
    def _adapt_js_code(self, code: str, source_repo: str, target_repo: str) -> str:
        """
        Adapt JavaScript/TypeScript code from source repo to target repo
        
        Args:
            code: Source JS/TS code
            source_repo: Name of source repository
            target_repo: Name of target repository
            
        Returns:
            Adapted JS/TS code
        """
        # Extract imports
        imports = self._extract_js_imports(code)
        
        # Build import mapping
        import_mapping = self._build_js_import_mapping(imports, source_repo, target_repo)
        
        # Replace imports
        adapted_code = code
        for old_import, new_import in import_mapping.items():
            if old_import == new_import:
                continue
            adapted_code = adapted_code.replace(old_import, new_import)
        
        return adapted_code
    
    def _extract_js_imports(self, code: str) -> List[str]:
        """
        Extract import statements from JS/TS code
        
        Args:
            code: JS/TS code
            
        Returns:
            List of import statements
        """
        imports = []
        # Match ES6 imports
        es6_imports = re.finditer(r'import\s+.*?from\s+[\'"](.+?)[\'"];?', code)
        for match in es6_imports:
            imports.append(match.group(0))
        
        # Match CommonJS requires
        cjs_imports = re.finditer(r'(?:const|let|var)\s+.*?=\s+require\([\'"](.+?)[\'"]\);?', code)
        for match in cjs_imports:
            imports.append(match.group(0))
            
        return imports
    
    def _build_js_import_mapping(
        self, imports: List[str], source_repo: str, target_repo: str
    ) -> Dict[str, str]:
        """
        Build mapping of imports from source to target repository
        
        Args:
            imports: List of import statements
            source_repo: Name of source repository
            target_repo: Name of target repository
            
        Returns:
            Dictionary mapping source imports to target imports
        """
        mapping = {}
        source_repo_obj = self.repo_manager.get_repository(source_repo)
        target_repo_obj = self.repo_manager.get_repository(target_repo)
        
        if not source_repo_obj or not target_repo_obj:
            return mapping
            
        # Extract source repo package name (assuming it matches the repo name)
        source_package = os.path.basename(source_repo_obj.root)
        target_package = os.path.basename(target_repo_obj.root)
        
        for imp in imports:
            # Replace internal imports
            if source_package in imp:
                mapping[imp] = imp.replace(source_package, target_package)
            else:
                mapping[imp] = imp
                
        return mapping
    
    def _adapt_generic_code(self, code: str, source_repo: str, target_repo: str) -> str:
        """
        Apply generic adaptations to code
        
        Args:
            code: Source code
            source_repo: Name of source repository
            target_repo: Name of target repository
            
        Returns:
            Adapted code
        """
        source_repo_obj = self.repo_manager.get_repository(source_repo)
        target_repo_obj = self.repo_manager.get_repository(target_repo)
        
        if not source_repo_obj or not target_repo_obj:
            return code
            
        # Extract source and target package names
        source_package = os.path.basename(source_repo_obj.root)
        target_package = os.path.basename(target_repo_obj.root)
        
        # Simple string replacement for package names
        adapted_code = code.replace(source_package, target_package)
        
        return adapted_code
    
    def detect_conflicts(self, code: str, target_repo: str) -> List[Dict]:
        """
        Detect potential conflicts when adapting code
        
        Args:
            code: Code to check for conflicts
            target_repo: Name of target repository
            
        Returns:
            List of conflict descriptions
        """
        conflicts = []
        target_repo_obj = self.repo_manager.get_repository(target_repo)
        
        if not target_repo_obj:
            return conflicts
            
        # This would require more sophisticated analysis
        # For now, return an empty list
        return conflicts
