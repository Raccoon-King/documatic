import os
import re
import sys
import json
import requests
from datetime import datetime
from urllib.parse import urljoin
import time

class APIDocumentation:
    def __init__(self, path, method, description, handler_func="", data_shapes=None):
        self.path = path
        self.method = method
        self.description = description or "Handler function"
        self.handler_func = handler_func
        self.data_shapes = data_shapes or []
        self.parameters = self._extract_parameters(path)
        self.framework = "unknown"
        self.curl_example = self._generate_curl_example()

    def _generate_curl_example(self):
        # Generate more sophisticated curl commands
        if self.method in ["GET", "HEAD"]:
            example = f"curl -X {self.method} {self.path}"
        elif self.method in ["POST", "PUT", "PATCH"]:
            example = f"curl -X {self.method} {self.path} -H \"Content-Type: application/json\" -d \"{{}}\""
        else:
            example = f"curl -X {self.method} {self.path}"

        return example

    def _extract_parameters(self, path):
        """Extract path parameters like :id, {id}, userId"""
        params = []

        # Pattern 1: :param (common in many frameworks)
        param_matches = re.finditer(r':(\w+)', path)
        for match in param_matches:
            param_name = match.group(1)
            params.append({
                'name': param_name,
                'type': 'string',
                'location': 'path',
                'example': self._get_param_example(param_name),
                'required': True
            })

        # Pattern 2: {param} (Gorilla Mux, Echo, etc.)
        param_matches = re.finditer(r'\{(\w+)\}', path)
        for match in param_matches:
            param_name = match.group(1)
            params.append({
                'name': param_name,
                'type': 'string',
                'location': 'path',
                'example': self._get_param_example(param_name),
                'required': True
            })

        return params

    def _get_param_example(self, param_name):
        """Generate appropriate example values for parameters"""
        examples = {
            'id': '123',
            'userId': '123',
            'user_id': '123',
            'articleId': '456',
            'postId': '789',
            'commentId': '101'
        }
        return examples.get(param_name.lower(), 'example_value')

    def _check_auth_required(self, input_text):
        """Check if authentication is mentioned in input text"""
        auth_keywords = ['auth', 'login', 'token', 'bearer', 'jwt', 'authorization', 'authenticated']
        return any(keyword in input_text.lower() for keyword in auth_keywords)

    def _check_rate_limited(self, input_text):
        """Check if rate limiting is mentioned in input text"""
        rate_keywords = ['rate limit', 'rate-limit', 'throttle', 'limit', 'quota']
        return any(keyword in input_text.lower() for keyword in rate_keywords)

class DataShape:
    def __init__(self, name, description="", shape="{}"):
        self.name = name
        self.description = description
        self.shape = shape

class GoCodeAnalyzer:
    def __init__(self):
        self.endpoints = []
        self.seen_endpoints = set()  # Track unique endpoints to prevent duplicates
        self.duplicate_tracker = {}  # Track all attempts to add endpoints
        self.duplicate_conflicts = []  # Store duplicate conflicts for reporting
        self.stats = {
            'files_processed': 0,
            'endpoints_found': 0,
            'duplicates_found': 0,
            'duplicates_skipped': 0,
            'frameworks_detected': set(),
            'errors': []
        }

    def analyze_directory(self, directory="."):
        """Enhanced directory analysis with better error handling and file filtering"""
        if not os.path.exists(directory):
            print(f"❌ Directory {directory} does not exist.")
            return []

        if not os.path.isdir(directory):
            print(f"❌ {directory} is not a directory.")
            return []

        go_files_found = 0
        total_files_processed = 0

        # Support for additional file extensions
        supported_extensions = ['.go']

        # Robust recursive search with better error handling
        try:
            for root, dirs, files in os.walk(directory):
                # Skip hidden directories and common excluded dirs
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'vendor', '_build']]

                for filename in files:
                    if any(filename.endswith(ext) for ext in supported_extensions) and not filename.endswith("_test.go"):
                        filepath = os.path.join(root, filename)

                        # Skip very large files (>10MB) to avoid memory issues
                        try:
                            file_size = os.path.getsize(filepath)
                            if file_size > 10 * 1024 * 1024:  # 10MB limit
                                print(f"⏭️ Skipping large file: {os.path.relpath(filepath, directory)} ({file_size//(1024*1024)}MB)")
                                continue
                        except (OSError, IOError) as e:
                            print(f"⚠️ Cannot access file size: {os.path.relpath(filepath, directory)} - {e}")
                            continue

                        # Get relative path for cleaner output
                        rel_path = os.path.relpath(filepath, directory)
                        print(f"🔍 Analyzing: {rel_path}")

                        try:
                            self._analyze_file(filepath)
                            go_files_found += 1
                            total_files_processed += 1
                        except Exception as e:
                            error_msg = f"Error analyzing {rel_path}: {str(e)}"
                            print(f"❌ {error_msg}")
                            self.stats['errors'].append(error_msg)

        except Exception as e:
            print(f"❌ Error walking directory {directory}: {e}")
            return []

        if go_files_found == 0:
            print(f"⚠️ No Go source files found in {directory}")
            print("💡 Hint: Make sure you're in the correct directory and source files aren't in excluded folders")
        else:
            print(f"✅ Successfully processed {go_files_found} Go files")
            self.stats['files_processed'] = total_files_processed
            # Don't overwrite endpoints_found as it's tracked during addition
            
            if self.stats['errors']:
                print(f"⚠️ Completed with {len(self.stats['errors'])} file errors (use verbose mode for details)")
            
            # Print duplicate statistics
            self._print_duplicate_stats()

        return self.endpoints
    
    def _print_duplicate_stats(self):
        """Print statistics about duplicates found"""
        if self.stats['duplicates_found'] > 0:
            print(f"\n📊 Duplicate Analysis:")
            print(f"   • Unique endpoints: {self.stats['endpoints_found']}")
            print(f"   • Duplicates detected: {self.stats['duplicates_found']}")
            print(f"   • Duplicates skipped: {self.stats['duplicates_skipped']}")
            
            if self.duplicate_conflicts:
                print(f"   • Conflicts resolved: {len(self.duplicate_conflicts)}")
                
                # Group by resolution type
                resolutions = {}
                for conflict in self.duplicate_conflicts:
                    res_type = conflict['resolution']
                    resolutions[res_type] = resolutions.get(res_type, 0) + 1
                
                for res_type, count in resolutions.items():
                    print(f"     - {res_type.replace('_', ' ').title()}: {count}")
        else:
            print(f"✅ No duplicate endpoints detected")
    
    def generate_duplicate_report(self):
        """Generate detailed duplicate report"""
        if not self.duplicate_conflicts:
            return "No duplicate endpoints detected.\n"
        
        report = "# Duplicate Endpoints Report\n\n"
        report += f"Found {len(self.duplicate_conflicts)} duplicate conflicts:\n\n"
        
        for i, conflict in enumerate(self.duplicate_conflicts, 1):
            report += f"## Conflict {i}: {conflict['method']} {conflict['path']}\n\n"
            report += f"**Existing:** `{conflict['existing']['handler']}` in `{conflict['existing']['file']}`\n"
            if conflict['existing']['description']:
                report += f"- Description: {conflict['existing']['description']}\n"
            
            report += f"**New:** `{conflict['new']['handler']}` in `{conflict['new']['file']}`\n"
            if conflict['new']['description']:
                report += f"- Description: {conflict['new']['description']}\n"
            
            report += f"**Resolution:** {conflict['resolution'].replace('_', ' ').title()}\n\n"
            report += "---\n\n"
        
        return report

    def _analyze_file(self, filepath):
        try:
            # Set current file for duplicate tracking
            self.current_file = os.path.basename(filepath)
            
            with open(filepath, "r", encoding="utf-8") as f:
                original_content = f.read()
                # Keep original content for comment extraction
                self.original_content = original_content
                # Remove comments to prevent matching commented-out code
                content = self._remove_comments(original_content)
                self._extract_http_handlefunc(content)
                self._extract_gin_routes(content)
                self._extract_echo_routes(content)
                self._extract_mux_routes(content)  # Add Gorilla Mux support
                self._extract_generic_methods(content)
        except Exception as e:
            print(f"Error analyzing {filepath}: {e}")
        finally:
            self.current_file = None

    def _remove_comments(self, content):
        """Remove Go-style comments to prevent matching commented code"""
        # More efficient comment removal using compiled regex
        if not hasattr(self, '_comment_patterns'):
            self._comment_patterns = [
                re.compile(r'//.*?$', re.MULTILINE),  # Single-line comments
                re.compile(r'/\*.*?\*/', re.DOTALL)    # Multi-line comments
            ]
        
        for pattern in self._comment_patterns:
            content = pattern.sub('', content)
        
        return content

    def _add_endpoint(self, endpoint):
        """Add endpoint if it's not a duplicate and passes validation"""
        # Validate endpoint
        if not self._validate_endpoint(endpoint):
            return
            
        endpoint_key = (endpoint.method, endpoint.path)
        
        # Track all attempts to add endpoints
        if endpoint_key not in self.duplicate_tracker:
            self.duplicate_tracker[endpoint_key] = []
        
        self.duplicate_tracker[endpoint_key].append({
            'endpoint': endpoint,
            'handler': endpoint.handler_func,
            'description': endpoint.description,
            'file': getattr(self, 'current_file', 'unknown')
        })
        
        # Check for duplicates
        if endpoint_key in self.seen_endpoints:
            self.stats['duplicates_found'] += 1
            self._handle_duplicate_endpoint(endpoint_key, endpoint)
            return
        
        # Add new endpoint
        self.seen_endpoints.add(endpoint_key)
        self.endpoints.append(endpoint)
        self.stats['endpoints_found'] += 1
            
    def _validate_endpoint(self, endpoint):
        """Validate endpoint data"""
        if not endpoint:
            return False
            
        # Validate path
        if not endpoint.path or not isinstance(endpoint.path, str):
            return False
            
        # Normalize and validate path
        endpoint.path = self._normalize_path(endpoint.path)
        if not endpoint.path.startswith('/'):
            return False
            
        # Path should not be too long (reasonable limit)
        if len(endpoint.path) > 500:
            return False
            
        # Validate method
        valid_methods = {'GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'}
        if endpoint.method not in valid_methods:
            return False
            
        # Sanitize description to prevent XSS in generated docs
        if endpoint.description:
            # Remove potential HTML/script tags
            endpoint.description = re.sub(r'<[^>]*>', '', endpoint.description)
            # Limit description length
            if len(endpoint.description) > 1000:
                endpoint.description = endpoint.description[:1000] + '...'
                
        return True
        
    def _normalize_path(self, path):
        """Normalize API path"""
        if not path:
            return ""
            
        # Remove extra whitespace
        path = path.strip()
        
        # Ensure path starts with /
        if not path.startswith('/'):
            path = '/' + path
            
        # Remove duplicate slashes
        path = re.sub(r'/+', '/', path)
        
        # Remove trailing slash unless it's the root path
        if len(path) > 1 and path.endswith('/'):
            path = path.rstrip('/')
            
        return path
    
    def _handle_duplicate_endpoint(self, endpoint_key, new_endpoint):
        """Handle duplicate endpoint detection and resolution"""
        method, path = endpoint_key
        existing_attempts = self.duplicate_tracker[endpoint_key]
        
        # Find the existing endpoint in our endpoints list
        existing_endpoint = None
        for ep in self.endpoints:
            if ep.method == method and ep.path == path:
                existing_endpoint = ep
                break
        
        if existing_endpoint:
            # Create conflict record
            conflict = {
                'method': method,
                'path': path,
                'existing': {
                    'handler': existing_endpoint.handler_func,
                    'description': existing_endpoint.description,
                    'file': existing_attempts[0]['file'] if existing_attempts else 'unknown'
                },
                'new': {
                    'handler': new_endpoint.handler_func,
                    'description': new_endpoint.description,
                    'file': getattr(self, 'current_file', 'unknown')
                },
                'resolution': 'kept_first'  # Default resolution strategy
            }
            
            # Apply conflict resolution strategy
            resolution = self._resolve_duplicate_conflict(existing_endpoint, new_endpoint, conflict)
            conflict['resolution'] = resolution
            
            if resolution == 'replace_with_new':
                # Replace existing endpoint with new one
                for i, ep in enumerate(self.endpoints):
                    if ep.method == method and ep.path == path:
                        self.endpoints[i] = new_endpoint
                        conflict['resolution'] = 'replaced_with_new'
                        break
            elif resolution == 'merge_descriptions':
                # Merge descriptions from both endpoints
                if new_endpoint.description and new_endpoint.description not in existing_endpoint.description:
                    existing_endpoint.description += f" | {new_endpoint.description}"
                    conflict['resolution'] = 'descriptions_merged'
            
            self.duplicate_conflicts.append(conflict)
            self.stats['duplicates_skipped'] += 1
            
            # Print warning
            print(f"⚠️ Duplicate endpoint: {method} {path}")
            print(f"   Existing: {existing_endpoint.handler_func} (in {conflict['existing']['file']})")
            print(f"   New: {new_endpoint.handler_func} (in {conflict['new']['file']})")
            print(f"   Resolution: {resolution}")
    
    def _resolve_duplicate_conflict(self, existing, new, conflict):
        """Determine how to resolve duplicate endpoint conflicts"""
        # Strategy 1: If new endpoint has better description, consider replacing
        if new.description and len(new.description) > len(existing.description or ''):
            if len(new.description) > 10:  # Meaningful description
                return 'replace_with_new'
        
        # Strategy 2: If handlers are different but similar path, merge descriptions
        if (existing.handler_func != new.handler_func and 
            existing.description and new.description):
            return 'merge_descriptions'
        
        # Strategy 3: If same handler in different files, might be legitimate
        if existing.handler_func == new.handler_func:
            return 'kept_first'  # Keep first occurrence
        
        # Default: Keep first endpoint found
        return 'kept_first'

    def _extract_http_handlefunc(self, content):
        # Find http.HandleFunc calls with more precise regex
        try:
            handle_func_pattern = r'http\.HandleFunc\s*\(\s*(["\'][^"\']*["\']|\`[^\`]*\`)\s*,\s*([^,)]+)\)'
            handle_func_matches = re.finditer(handle_func_pattern, content)
            
            for match in handle_func_matches:
                try:
                    path = self._clean_string_arg(match.group(1))
                    handler_func = self._clean_string_arg(match.group(2))

                    # Validate path
                    if not path or not path.startswith('/'):
                        continue
                        
                    # Look for comments above the call
                    description = self._find_function_comment(content, handler_func, match.start())

                    if path and handler_func:
                        endpoint = APIDocumentation(
                            path=path,
                            method="GET",  # HandleFunc typically handles GET
                            description=description,
                            handler_func=handler_func
                        )
                        self._add_endpoint(endpoint)
                except Exception as e:
                    print(f"⚠️ Error processing HandleFunc match: {e}")
                    continue
                    
        except Exception as e:
            print(f"⚠️ Error in _extract_http_handlefunc: {e}")

    def _extract_gin_routes(self, content):
        # Gin router patterns: router.GET, router.POST, etc.
        methods = [
            'GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'
        ]

        # Group-based routes: router.Group("/api").GET("/users", handler)
        # Direct method calls: router.GET("/users", handler)

        for method in methods:
            try:
                # Direct method calls with better regex
                pattern = rf'\w+\.{method}\s*\(\s*(["\'][^"\']*["\']|\`[^\`]*\`)\s*,\s*([^,)]+)\)'
                matches = re.finditer(pattern, content)
                for match in matches:
                    try:
                        path = self._clean_string_arg(match.group(1))
                        handler_func = self._clean_string_arg(match.group(2))

                        # Validate path
                        if path and path.startswith('/') and handler_func:
                            description = self._find_function_comment(content, handler_func, match.start())
                            endpoint = APIDocumentation(
                                path=path,
                                method=method,
                                description=description,
                                handler_func=handler_func
                            )
                            self._add_endpoint(endpoint)
                    except Exception as e:
                        print(f"⚠️ Error processing {method} route: {e}")
                        continue
            except Exception as e:
                print(f"⚠️ Error processing {method} routes: {e}")

            # Handle method calls: router.Handle("GET", "/path", handler)
            pattern = rf'\w+\.Handle\s*\(\s*["\']({method})["\']\s*,\s*([^,]+)\s*,\s*([^)]+)\)'
            matches = re.finditer(pattern, content)
            for match in matches:
                method_name = match.group(1)
                path = self._clean_string_arg(match.group(2))
                handler_func = self._clean_string_arg(match.group(3))

                if path:
                    description = self._find_function_comment(content, handler_func, match.start())
                    endpoint = APIDocumentation(
                        path=path,
                        method=method_name,
                        description=description,
                        handler_func=handler_func
                    )
                    self._add_endpoint(endpoint)

    def _extract_echo_routes(self, content):
        # Echo router patterns: e.GET, e.POST, etc.
        methods = [
            'GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'
        ]

        for method in methods:
            # Echo method calls like e.POST("/users", handler)
            pattern = rf'\w+\.{method}\s*\(\s*([^,]+)\s*,\s*([^)]+)\)'
            matches = re.finditer(pattern, content)
            for match in matches:
                path = self._clean_string_arg(match.group(1))
                handler_func = self._clean_string_arg(match.group(2))

                if path:
                    description = self._find_function_comment(content, handler_func, match.start())
                    endpoint = APIDocumentation(
                        path=path,
                        method=method,
                        description=description,
                        handler_func=handler_func
                    )
                    self._add_endpoint(endpoint)

    def _extract_mux_routes(self, content):
        # Gorilla Mux router patterns - Enhanced with better detection

        # Pattern 1: r.HandleFunc("/path", handler).Methods("GET", "POST")
        mux_pattern1 = r'\w+\.HandleFunc\s*\(\s*([^,]+)\s*,\s*([^)]+)\)\s*\.Methods\s*\(\s*([^)]+)\s*\)'
        matches1 = re.finditer(mux_pattern1, content)

        # Pattern 2: records.HandleFunc("/path", handler).Methods(GET)
        mux_pattern2 = r'\w+\.HandleFunc\s*\(\s*([^,]+)\s*,\s*([^)]+)\)\s*\.Methods\s*\(\s*([^)]+)\s*\)'
        matches2 = re.finditer(mux_pattern2, content)

        # Combine all matches
        all_matches = list(matches1)
        all_matches.extend([m for m in matches2 if m.start() not in [original.start() for original in matches1]])

        for match in all_matches:
            path = self._clean_string_arg(match.group(1))
            handler_func = self._clean_string_arg(match.group(2))
            methods_str = match.group(3)

            # Extract methods from the .Methods call
            # Handle both "GET" and GET (constants vs strings)
            method_matches = re.finditer(r'["\']([A-Z]+)["\']|(\b[A-Z]{3,7}\b)', methods_str)
            methods_found = []
            for method_match in method_matches:
                method = method_match.group(1) or method_match.group(2)
                if method in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']:
                    methods_found.append(method)

            if not methods_found:
                methods_found = ['GET']  # Default to GET if no specific method found

            for method in methods_found:
                if path:
                    description = self._find_function_comment(content, handler_func, match.start())
                    if not description or description.strip() == "":
                        description = "Router endpoint"
                    endpoint = APIDocumentation(
                        path=path,
                        method=method,
                        description=f"{description} - Gorilla Mux Handler",
                        handler_func=handler_func
                    )
                    self._add_endpoint(endpoint)

        # Pattern 3: r.Path("/path").HandlerFunc(handler).Methods("GET")
        mux_pattern_path = r'\w+\.Path\s*\(\s*([^)]+)\)\s*\.HandlerFunc\s*\(\s*([^)]+)\)\s*\.Methods\s*\(\s*([^)]+)\s*\)'
        matches = re.finditer(mux_pattern_path, content)
        for match in matches:
            path = self._clean_string_arg(match.group(1))
            handler_func = self._clean_string_arg(match.group(2))
            methods_str = match.group(3)

            method_matches = re.finditer(r'["\']([A-Z]+)["\']|(\b[A-Z]{3,7}\b)', methods_str)
            methods_found = []
            for method_match in method_matches:
                method = method_match.group(1) or method_match.group(2)
                if method in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']:
                    methods_found.append(method)

            if not methods_found:
                methods_found = ['GET']  # Default to GET

            for method in methods_found:
                if path:
                    description = self._find_function_comment(content, handler_func, match.start())
                    if not description or description.strip() == "":
                        description = "Path-handler endpoint"
                    endpoint = APIDocumentation(
                        path=path,
                        method=method,
                        description=f"{description} - Gorilla Mux Path Handler",
                        handler_func=handler_func
                    )
                    self._add_endpoint(endpoint)

        # Pattern 4: HandleFunc without Methods (could be Mux without explicit methods)
        mux_pattern_simple = r'\w+\.HandleFunc\s*\(\s*([^,]+)\s*,\s*([^)]+)\)'
        matches = re.finditer(mux_pattern_simple, content)
        for match in matches:
            # Check if the router variable looks like a Gorilla Mux router
            router_var = content[:match.start()].strip().split('\n')[-1]
            if '=' in router_var and ('mux.NewRouter()' in router_var or '.HandleFunc' in content[max(0, match.start()-200):match.start()]):
                path = self._clean_string_arg(match.group(1))
                handler_func = self._clean_string_arg(match.group(2))

                # Skip if this is followed by .Methods (already handled above)
                if '.Methods(' in content[match.end():match.end()+50]:
                    continue

                if path:
                    description = self._find_function_comment(content, handler_func, match.start())
                    if not description or description.strip() == "":
                        description = "Router endpoint"
                    endpoint = APIDocumentation(
                        path=path,
                        method="GET",  # Default assumption for HandleFunc
                        description=f"{description} - Gorilla Mux HandleFunc",
                        handler_func=handler_func
                    )
                    self._add_endpoint(endpoint)

    def _extract_generic_methods(self, content):
        # Generic router patterns for other frameworks
        # This catches method calls that might not be specifically Gin, Echo, or Mux
        router_patterns = {
            r'\w+\.(GET|POST|PUT|DELETE|PATCH)\s*\(\s*([^,]+)\s*,\s*([^)]+)\)': lambda m: (m.group(1), m.group(2), m.group(3)),
        }

        for pattern, extractor in router_patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                method, path_str, handler_func = extractor(match)
                path = self._clean_string_arg(path_str)
                handler_func = self._clean_string_arg(handler_func)

                if path and method not in ['Gin', 'Echo', 'Mux']:  # Avoid duplication
                    description = self._find_function_comment(content, handler_func, match.start())
                    endpoint = APIDocumentation(
                        path=path,
                        method=method.upper(),
                        description=description,
                        handler_func=handler_func
                    )
                    self._add_endpoint(endpoint)

    def _clean_string_arg(self, arg):
        """Clean and extract string literals from Go code"""
        if not arg:
            return ""
            
        arg = arg.strip()
        
        # Handle quoted strings (double or single quotes)
        if len(arg) >= 2:
            if (arg.startswith('"') and arg.endswith('"')) or \
               (arg.startswith("'") and arg.endswith("'")):
                # Remove outer quotes and handle escaped quotes
                inner = arg[1:-1]
                # Unescape common escape sequences
                inner = inner.replace('\\"', '"').replace("\\'", "'")
                inner = inner.replace('\\n', '\n').replace('\\t', '\t')
                return inner
                
        # Handle backtick strings (Go raw strings)
        if arg.startswith('`') and arg.endswith('`') and len(arg) >= 2:
            return arg[1:-1]
            
        return arg

    def _find_function_comment(self, content, func_name, call_position):
        """Find comments for a function using original content with comments"""
        # Use original content to preserve comments
        if hasattr(self, 'original_content') and self.original_content:
            content = self.original_content
        
        lines = content[:call_position].split('\n')
        comment_lines = []

        # Look backwards from the call position
        for line in reversed(lines[-10:]):  # Only check last 10 lines for performance
            line = line.strip()
            if line.startswith('//'):
                comment_text = line[2:].strip()
                # Skip empty comments or comments that look like code
                if comment_text and not any(keyword in comment_text.lower() 
                                          for keyword in ['http.', 'router.', 'func(']):
                    comment_lines.insert(0, comment_text)
            elif line.startswith('func') and func_name in line:
                break
            elif line and not line.startswith('//') and comment_lines:
                # Stop if we hit non-comment code after finding comments
                break

        if comment_lines:
            return ' '.join(comment_lines)
        return ""

class DataInspector:
    """Inspects running servers to get actual data shapes"""

    def __init__(self):
        self.base_url = None
        self.server_found = False

    def find_running_server(self, port):
        """Connect to a running Go server on specified port"""
        try:
            url = f"http://localhost:{port}"
            response = requests.get(f"{url}/health", timeout=3)
            if response.status_code in [200, 404]:  # 404 means server is running but no /health endpoint
                self.base_url = url
                self.server_found = True
                print(f" ✅ Connected to server at {url}")
                return True
            else:
                print(f" ❌ Server responded but with unexpected status: {response.status_code}")
                return False
        except requests.RequestException as e:
            print(f" ❌ Could not connect to server at localhost:{port}")
            print(f"    Error: {e}")
            return False

    def get_endpoint_data(self, endpoints):
        """Get actual data shapes from running server endpoints"""
        if not self.server_found:
            print(" ⚠️  No server available for data inspection")
            return

        print("\n🔬 Inspecting server endpoints for data shapes...\n")
        inspected_count = 0

        for endpoint in endpoints:
            if endpoint.method == "GET" or (endpoint.method in ['POST', 'PUT'] and 'create' in endpoint.path.lower()):
                try:
                    if self._inspect_endpoint(endpoint):
                        inspected_count += 1
                except Exception as e:
                    print(f"    ⚠️  Failed to inspect {endpoint.path}: {e}")

        print(f"🎯 Successfully inspected {inspected_count} endpoints")

    def _inspect_endpoint(self, endpoint):
        """Inspect a single endpoint to get data shape"""
        try:
            if endpoint.method == "GET":
                # For GET endpoints, just request the data
                response = requests.get(urljoin(self.base_url, endpoint.path), timeout=5)
                if response.status_code == 200 and response.headers.get('content-type', '').startswith('application/json'):
                    return self._parse_json_response(endpoint, response.json(), "Response")
                elif response.status_code == 200:
                    # Non-JSON response
                    endpoint.data_shapes.append(DataShape(
                        "Response",
                        f"Status {response.status_code}",
                        "text/plain"
                    ))

            elif endpoint.method == "POST" and 'users' in endpoint.path.lower():
                # For POST to user endpoints, send sample JSON
                sample_data = {
                    "name": "Sample User",
                    "email": "sample@example.com"
                }

                headers = {'Content-Type': 'application/json'}
                response = requests.post(
                    urljoin(self.base_url, endpoint.path),
                    json=sample_data,
                    headers=headers,
                    timeout=5
                )

                if response.status_code in [200, 201]:
                    endpoint.data_shapes.append(DataShape(
                        "Request",
                        "User creation data",
                        json.dumps(sample_data, indent=2)
                    ))

                    if response.headers.get('content-type', '').startswith('application/json'):
                        return self._parse_json_response(endpoint, response.json(), "Response")

            return False

        except requests.RequestException:
            return False

    def _parse_json_response(self, endpoint, response_data, shape_type):
        """Parse JSON response to generate data shape documentation"""
        try:
            # Handle different response types
            if isinstance(response_data, dict):
                self._process_dict_response(endpoint, response_data, shape_type)
            elif isinstance(response_data, list):
                self._process_list_response(endpoint, response_data, shape_type)
            else:
                # Simple value
                if shape_type == "Response":
                    shape_desc = f"Simple {type(response_data).__name__} response"
                    example = json.dumps(response_data, indent=2)[:200] + "..."
                    endpoint.data_shapes.append(DataShape(shape_type, shape_desc, example))

            return True

        except Exception as e:
            print(f"    Error parsing JSON for {endpoint.path}: {e}")
            return False

    def _process_dict_response(self, endpoint, data, shape_type):
        """Process dictionary response to create JSON schema example"""
        # Create a more readable JSON example
        example = json.dumps(data, indent=2)

        if shape_type == "Response":
            # Try to infer meaningful descriptions
            if "status" in data:
                shape_desc = "Status response"
            elif "users" in str(endpoint.path).lower():
                shape_desc = "User data response"
            elif "error" in data:
                shape_desc = "Error response"
            else:
                shape_desc = "Data object response"

        endpoint.data_shapes.append(DataShape(
            shape_type,
            shape_desc,
            example
        ))

    def _process_list_response(self, endpoint, data, shape_type):
        """Process list response to create JSON schema example"""
        if not data:
            # Empty list
            endpoint.data_shapes.append(DataShape(
                shape_type,
                "Empty array response",
                "[]"
            ))
            return

        # Show first item as example for non-empty lists
        if isinstance(data[0], dict):
            example_data = [data[0]] if len(data) > 0 else []
            example = json.dumps(example_data, indent=2)

            if shape_type == "Response":
                if "users" in str(endpoint.path).lower():
                    shape_desc = "Array of user objects"
                else:
                    shape_desc = f"Array of {len(data)} items"
        else:
            # Simple array
            limited_data = data[:3] if len(data) > 3 else data
            example = json.dumps(limited_data, indent=2)
            shape_desc = f"Array of {len(data)} {type(data[0]).__name__} values"

        endpoint.data_shapes.append(DataShape(
            shape_type,
            shape_desc,
            example
        ))

def generate_markdown_docs(endpoints, output_file="apidocs.md"):
    """Generate comprehensive, visually enhanced markdown documentation"""

    # Sort endpoints by path for better organization
    endpoints = sorted(endpoints, key=lambda x: x.path)

    # Group by base path (everything before the first /)
    grouped_endpoints = {}
    for endpoint in endpoints:
        if endpoint.path == "/":
            base = "/"
        else:
            base_parts = endpoint.path.strip("/").split("/")
            base = f"/{base_parts[0]}" if base_parts else "/"
        if base not in grouped_endpoints:
            grouped_endpoints[base] = []
        grouped_endpoints[base].append(endpoint)

    # Get method count statistics for badges
    method_counts = {}
    for endpoint in endpoints:
        method_counts[endpoint.method] = method_counts.get(endpoint.method, 0) + 1

    def get_method_badge(method):
        """Return emoji and colored badge for HTTP method"""
        badges = {
            'GET': '🟢 GET',
            'POST': '🔵 POST',
            'PUT': '🟡 PUT',
            'DELETE': '🔴 DELETE',
            'PATCH': '🟠 PATCH',
            'OPTIONS': '⚪ OPTIONS',
            'HEAD': '⚫ HEAD'
        }
        return badges.get(method, f'⚫ {method}')

    with open(output_file, "w", encoding="utf-8") as f:
        # Enhanced Header with Visual Appeal
        f.write("# 🚀 API Documentation\n\n")
        f.write("**Generated by Go Code Analyzer** • ")
        f.write(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} • ")
        f.write("⚡ Auto-generated from source code\n\n")

        # Project Status Badge
        total_endpoints = len(endpoints)
        status_emoji = "🟢" if total_endpoints > 0 else "⚪"
        status_msg = "Ready" if total_endpoints > 0 else "No endpoints found"
        endpoints_info = ""
        if total_endpoints > 0:
            endpoints_info = " %.2f" % (total_endpoints / len(endpoints) * 100)
        f.write(f"{status_emoji} **Status**: {status_msg}{endpoints_info}%\n\n")

        # Quick Stats Overview
        f.write("---\n\n## 📊 API Overview\n\n")
        f.write("| Metric | Value |\n")
        f.write("|---|-----|\n")
        f.write(f"| 🔗 **Total Endpoints** | {total_endpoints} |\n")
        f.write(f"| 📁 **Route Groups** | {len(grouped_endpoints)} |\n")
        f.write(f"| 🔧 **HTTP Methods** | {len(method_counts)} |\n")
        f.write("|---|---|\n\n")

        # Method Distribution Badges
        if method_counts:
            f.write("### HTTP Method Distribution\n\n")
            method_badges = [f"{get_method_badge(method)}: {count}" for method, count in sorted(method_counts.items())]
            f.write(" | ".join(method_badges))
            f.write("\n\n")

        # Enhanced Table of Contents
        f.write("---\n\n## 📚 Table of Contents\n\n")
        for i, (base_path, group_endpoints) in enumerate(sorted(grouped_endpoints.items()), 1):
            folder_emoji = "📁" if base_path != "/" else "🏠"
            f.write(f"### {i}. {folder_emoji} {base_path.upper() or 'ROOT'}\n\n")

            # Create endpoint table for each group
            if group_endpoints:
                f.write("| Method | Path | Handler | Quick Test |\n")
                f.write("|--------|------|---------|------------|\n")

                for endpoint in group_endpoints[:10]:  # Show first 10 endpoints, link to more
                    curl_short = endpoint.curl_example.replace("curl ", "").replace("http://localhost:8080", "")
                    f.write(f"| {get_method_badge(endpoint.method)} | `{endpoint.path}` | `{endpoint.handler_func}` | `curl {curl_short}` |\n")

                if len(group_endpoints) > 10:
                    anchor = base_path.replace('/', '').lower() or 'root'
                    f.write(f"[...] **{len(group_endpoints) - 10} more endpoints** - [{base_path}](#{anchor})\n\n")
                else:
                    f.write("\n")
            f.write("\n")

        f.write("---\n\n")

        # Quick Usage Guide
        f.write("## 🚀 Quick Start\n\n")
        f.write("### Running the API\n")
        f.write("```bash\n# Start your Go server\ngo run main.go\n```\n\n")

        f.write("### Testing Endpoints\n")
        if endpoints[:5]:  # Show first 5 examples
            for endpoint in endpoints[:5]:
                f.write(f"```bash\n{endpoint.curl_example}\n```\n")

        f.write("---\n\n")

        # Detailed Endpoint Documentation
        f.write("## 🔧 Detailed Endpoint Documentation\n\n")
        f.write("<details>\n<summary>📖 Click to expand detailed endpoint documentation</summary>\n\n")

        for base_path, group_endpoints in sorted(grouped_endpoints.items()):
            folder_emoji = "📁" if base_path != "/" else "🏠"
            anchor = base_path.replace('/', '').lower() or 'root'
            f.write(f"### {folder_emoji} {base_path.upper() or 'ROOT'} Endpoints\n\n")

            for endpoint in group_endpoints:
                # Enhanced endpoint header with badges
                f.write(f"<details>\n<summary>{get_method_badge(endpoint.method)} `{endpoint.path}`</summary>\n\n")

                f.write("**📝 Overview**\n")
                f.write("| Property | Value |\n")
                f.write("|---|-----|\n")
                f.write(f"| 🔧 Handler | `{endpoint.handler_func}` |\n")
                f.write(f"| 📖 Description | {endpoint.description or 'Handler function'} |\n")

                f.write("\n**🧪 Testing**\n")
                f.write(f"```bash\n{endpoint.curl_example}\n```\n")

                # Expected Response Examples
                f.write("\n**💡 Expected Response**\n")
                if "health" in endpoint.path.lower():
                    f.write("```json\n{\"status\": \"ok\"}\n```\n")
                elif "users" in endpoint.path.lower():
                    if endpoint.method == "GET":
                        f.write("```json\n[\n  {\n    \"id\": 1,\n    \"name\": \"John Doe\",\n    \"email\": \"john@example.com\"\n  }\n]\n```\n")
                    elif endpoint.method == "POST":
                        f.write("```json\n{\n  \"id\": 3,\n  \"name\": \"New User\",\n  \"email\": \"new@example.com\"\n}\n```\n")
                else:
                    f.write("```json\n{\n  \"message\": \"Success response\"\n}\n```\n")

                if endpoint.data_shapes:
                    f.write("\n**📊 Data Shapes**\n")
                    for shape in endpoint.data_shapes:
                        f.write(f"#### {shape.name}\n")
                        f.write(f"**Description**: {shape.description}\n\n")
                        f.write("```json\n" + shape.shape + "\n```\n")
                    f.write("\n")

                f.write("</details>\n\n")

            f.write("\n---\n\n")

        f.write("</details>\n\n")

        # Enhanced Summary with Visual Improvements
        f.write("## 📈 Comprehensive Statistics\n\n")

        # Progress Bar Visualization (ASCII style)
        f.write("### HTTP Method Distribution\n\n")
        max_count = max(method_counts.values()) if method_counts else 1

        for method, count in sorted(method_counts.items()):
            percentage = count / len(endpoints) * 100
            bar_length = int((count / max_count) * 30)  # 30 character bars
            plural = "s" if count != 1 else ""
            f.write(f"**{get_method_badge(method)}**: {count} endpoint{plural}")
            filled_bar = "█" * bar_length
            empty_bar = "░" * (30 - bar_length)
            f.write(f" {filled_bar}{empty_bar} {percentage:.1f}%\n")

        # Endpoint Quality Metrics
        f.write("\n### 📊 API Quality Metrics\n\n")
        documented_endpoints = sum(1 for ep in endpoints if ep.description and ep.description != "Handler function")
        documentation_coverage = (documented_endpoints / len(endpoints)) * 100 if endpoints else 0

        f.write("| Metric | Value |\n")
        f.write("|---|-----|\n")
        f.write(f"| 📊 **Documentation Coverage** | {documentation_coverage:.1f}% |\n")
        f.write(f"| � **Documented Endpoints** | {documented_endpoints}/{len(endpoints)} |\n")
        f.write(f"| �🚀 **REST-compliant** | Yes (HTTP methods + paths) |\n")
        f.write("| 📋 **Generator Version** | 2.0 - Enhanced |\n")
        f.write("|---|---|\n\n")

        # Footer
        f.write("---\n\n")
        f.write("## 💡 Tips & Best Practices\n\n")
        f.write("- 🧪 **Test endpoints** with the provided curl commands\n")
        f.write("- 📖 **Add more documentation** by including comments above your handlers\n")
        f.write("- 🎯 **Follow REST conventions** for better API design\n")
        f.write("- 🔧 **Regenerate docs** whenever you add new endpoints\n")
        f.write("\n\n---\n\n")
        f.write("*📄 This documentation was auto-generated by the Go Code API Documentation Generator.*\n")
        f.write("*🤖 Last updated: " + datetime.now().strftime('%A, %B %d, %Y at %I:%M %p') + "*\n")
        f.write("")

def print_ascii_art():
    """Print ASCII art logo for Grabby Documatic"""
    # Main title
    title = r"""
 ██████╗ ██████╗  █████╗ ██████╗ ██████╗ ██╗   ██╗
██╔════╝ ██╔══██╗██╔══██╗██╔══██╗██╔══██╗╚██╗ ██╔╝
██║  ███╗██████╔╝███████║██████╔╝██████╔╝ ╚████╔╝ 
██║   ██║██╔══██╗██╔══██║██╔══██╗██╔══██╗  ╚██╔╝  
╚██████╔╝██║  ██║██║  ██║██████╔╝██████╔╝   ██║   
 ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚═════╝    ╚═╝   
                                                   
██████╗  ██████╗  ██████╗██╗   ██╗███╗   ███╗ █████╗ ████████╗██╗ ██████╗
██╔══██╗██╔═══██╗██╔════╝██║   ██║████╗ ████║██╔══██╗╚══██╔══╝██║██╔════╝
██║  ██║██║   ██║██║     ██║   ██║██╔████╔██║███████║   ██║   ██║██║     
██║  ██║██║   ██║██║     ██║   ██║██║╚██╔╝██║██╔══██║   ██║   ██║██║     
██████╔╝╚██████╔╝╚██████╗╚██████╔╝██║ ╚═╝ ██║██║  ██║   ██║   ██║╚██████╗
╚═════╝  ╚═════╝  ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝
    """
    
    print(title)
    print("🦝 Your Friendly Go API Documentation Generator 📚")
    print("=" * 70)

def print_mascot(style="working"):
    """Print simple raccoon emoji messages"""
    messages = {
        "working": "🦝 Working hard on your docs! ☕",
        "success": "🦝 Documentation ready! 🎉",
        "analyzing": "🦝 Analyzing your Go code... 🔍",
        "duplicate": "🦝 Found duplicates! ⚠️",
        "goodbye": "🦝 Thanks for using Grabby-Documatic! 👋"
    }
    
    if style in messages:
        print(f"\n{messages[style]}\n")
    else:
        print(f"\n{messages['working']}\n")

def display_main_menu():
    """Display the main menu options"""
    print("\n📋 What would you like to do?")
    print("1. 📁 Analyze Go project directory")
    print("2. 🔬 Analyze with live server inspection")
    print("3. 📊 Generate duplicate endpoints report")
    print("4. ⚙️  Advanced settings")
    print("5. ❓ Help & Info")
    print("6. 🚪 Exit")
    return input("\nSelect an option (1-6): ").strip()

def get_directory_input():
    """Get directory input from user"""
    print("\n📂 Directory Selection:")
    print("Press Enter for current directory, or enter in the full path:")
    directory = input("Directory path [current]: ").strip()
    return directory if directory else "."

def get_server_port():
    """Get server port for inspection"""
    while True:
        print("\n🔬 Server Inspection Setup:")
        port_input = input("Enter server port (press Enter to skip): ").strip()
        
        if not port_input:
            return None
            
        try:
            port = int(port_input)
            if 1 <= port <= 65535:
                return port
            else:
                print("❌ Port must be between 1 and 65535")
        except ValueError:
            print("❌ Please enter a valid port number")

def confirm_action(message):
    """Get yes/no confirmation from user"""
    while True:
        response = input(f"{message} (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Please enter 'y' or 'n'")

def display_settings_menu():
    """Display advanced settings menu"""
    print("\n⚙️ Advanced Settings:")
    print("1. 🔄 Toggle recursive directory scanning")
    print("2. 📝 Configure duplicate resolution strategy")
    print("3. 🎯 Set output file names")
    print("4. 🔙 Back to main menu")
    return input("Select setting (1-4): ").strip()

def run_analysis(directory, config, server_port=None):
    """Run the main analysis with given parameters"""
    print_mascot("analyzing")
    print(f"\n🔍 Starting analysis of: {directory}")
    print("-" * 50)
    
    # Create analyzer
    analyzer = GoCodeAnalyzer()
    analyzer.enable_recursive = config['recursive']
    
    # Run analysis
    endpoints = analyzer.analyze_directory(directory)
    
    if not endpoints:
        print("⚠️ No API endpoints found in the Go files.")
        return None
    
    # Server inspection if requested
    inspector = None
    if server_port:
        print(f"\n🔬 Attempting to connect to server on port {server_port}...")
        inspector = DataInspector()
        server_found = inspector.find_running_server(server_port)
        
        if server_found:
            inspector.get_endpoint_data(endpoints)
            print("✅ Server data inspection completed!")
        else:
            print("❌ Could not connect to server")
    
    # Generate documentation
    generate_markdown_docs(endpoints, config['output_file'])
    print(f"✅ Generated {config['output_file']} with {len(endpoints)} endpoints")
    
    # Generate duplicate report if there were conflicts
    if analyzer.duplicate_conflicts:
        print_mascot("duplicate")
        duplicate_report = analyzer.generate_duplicate_report()
        with open(config['duplicate_report_file'], "w", encoding="utf-8") as f:
            f.write(duplicate_report)
        print(f"📊 Duplicate report saved to {config['duplicate_report_file']}")
    
    # Show success mascot
    print_mascot("success")
    
    # Print summary
    method_counts = {}
    for endpoint in endpoints:
        method_counts[endpoint.method] = method_counts.get(endpoint.method, 0) + 1
    
    if method_counts:
        print("\n📊 Analysis Summary:")
        for method, count in sorted(method_counts.items()):
            print(f"   {method}: {count} endpoints")
    
    # Server inspection stats
    if inspector and inspector.server_found:
        inspected_endpoints = sum(1 for ep in endpoints if len(ep.data_shapes) > 0)
        print(f"\n🔬 Server Inspection Results:")
        print(f"   📶 Server URL: {inspector.base_url}")
        print(f"   🎯 Inspected: {inspected_endpoints}/{len(endpoints)} endpoints")
    
    return endpoints

def show_help():
    """Display help information"""
    print("\n❓ Help & Information:")
    print("=" * 40)
    print("🎯 Purpose: Generate comprehensive API documentation from Go source code")
    print("📁 Supported frameworks: Gin, Echo, Gorilla Mux, net/http")
    print("🔍 Features:")
    print("   • Automatic endpoint discovery")
    print("   • Duplicate detection and resolution")
    print("   • Live server data inspection")
    print("   • Recursive directory scanning")
    print("   • Comprehensive markdown documentation")
    print("\n💡 Tips:")
    print("   • Ensure your Go files are in the selected directory")
    print("   • For server inspection, make sure your server is running")
    print("   • Check generated files for documentation results")
    
def main():
    # Configuration state
    config = {
        'recursive': True,
        'duplicate_strategy': 'keep_first',
        'output_file': 'apidocs.md',
        'duplicate_report_file': 'duplicates_report.md'
    }
    
    # Clear screen and show ASCII art
    print("\033[2J\033[H", end="")  # Clear screen
    print_ascii_art()
    
    while True:
        choice = display_main_menu()
        
        if choice == '1':  # Analyze directory
            directory = get_directory_input()
            if confirm_action(f"📁 Analyze directory '{directory}'?"):
                run_analysis(directory, config)
                input("\nPress Enter to continue...")
                
        elif choice == '2':  # Analyze with server inspection
            directory = get_directory_input()
            port = get_server_port()
            if port and confirm_action(f"🔬 Analyze '{directory}' with server inspection on port {port}?"):
                run_analysis(directory, config, port)
                input("\nPress Enter to continue...")
                
        elif choice == '3':  # Generate duplicate report only
            directory = get_directory_input()
            if confirm_action(f"📊 Generate duplicate report for '{directory}'?"):
                analyzer = GoCodeAnalyzer()
                analyzer.analyze_directory(directory)
                duplicate_report = analyzer.generate_duplicate_report()
                with open(config['duplicate_report_file'], "w", encoding="utf-8") as f:
                    f.write(duplicate_report)
                print(f"✅ Duplicate report saved to {config['duplicate_report_file']}")
                input("\nPress Enter to continue...")
                
        elif choice == '4':  # Settings
            settings_choice = display_settings_menu()
            
            if settings_choice == '1':  # Toggle recursive
                config['recursive'] = not config['recursive']
                status = "ENABLED" if config['recursive'] else "DISABLED"
                print(f"🔄 Recursive scanning: {status}")
                
            elif settings_choice == '2':  # Duplicate strategy
                print(f"\n📝 Current strategy: {config['duplicate_strategy']}")
                print("Available strategies:")
                print("1. keep_first - Keep first occurrence")
                print("2. replace_with_new - Replace with newer/better description")
                print("3. merge_descriptions - Combine descriptions")
                choice = input("Select (1-3): ").strip()
                strategies = {'1': 'keep_first', '2': 'replace_with_new', '3': 'merge_descriptions'}
                if choice in strategies:
                    config['duplicate_strategy'] = strategies[choice]
                    print(f"✅ Strategy updated to: {config['duplicate_strategy']}")
                    
            elif settings_choice == '3':  # Output files
                new_output = input(f"Output file [{config['output_file']}]: ").strip()
                if new_output:
                    config['output_file'] = new_output
                new_dup_output = input(f"Duplicate report file [{config['duplicate_report_file']}]: ").strip()
                if new_dup_output:
                    config['duplicate_report_file'] = new_dup_output
                print("✅ Output files updated")
                
            input("Press Enter to continue...")
                
        elif choice == '5':  # Help
            show_help()
            input("\nPress Enter to continue...")
            
        elif choice == '6':  # Exit
            print_mascot("goodbye")
            print("\n👋 Thank you for using Grabby Documatic!")
            print("📚 Happy documenting!")
            break
            
        else:
            print("❌ Invalid option. Please select 1-6.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
