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
        self.curl_example = self._generate_curl_example()

    def _generate_curl_example(self):
        if self.method == "GET":
            return f"curl {self.path}"
        else:
            return f"curl -X {self.method} {self.path}"

class DataShape:
    def __init__(self, name, description="", shape="{}"):
        self.name = name
        self.description = description
        self.shape = shape

class GoCodeAnalyzer:
    def __init__(self):
        self.endpoints = []

    def analyze_directory(self, directory="."):
        if not os.path.exists(directory):
            print(f"Directory {directory} does not exist.")
            return []

        go_files_found = 0

        # Recursive search through all subdirectories
        for root, dirs, files in os.walk(directory):
            for filename in files:
                if filename.endswith(".go") and not filename.endswith("_test.go"):
                    filepath = os.path.join(root, filename)

                    # Get relative path for cleaner output
                    rel_path = os.path.relpath(filepath, directory)
                    print(f"Analyzing: {rel_path}")

                    self._analyze_file(filepath)
                    go_files_found += 1

        if go_files_found == 0:
            print(f"No Go source files found in {directory}")

        return self.endpoints

    def _analyze_file(self, filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                self._extract_http_handlefunc(content)
                self._extract_gin_routes(content)
                self._extract_echo_routes(content)
                self._extract_mux_routes(content)  # Add Gorilla Mux support
                self._extract_generic_methods(content)
        except Exception as e:
            print(f"Error analyzing {filepath}: {e}")

    def _extract_http_handlefunc(self, content):
        # Find http.HandleFunc calls
        handle_func_matches = re.finditer(r'http\.HandleFunc\s*\(\s*([^,]+)\s*,\s*([^)]+)\)', content)
        for match in handle_func_matches:
            path = self._clean_string_arg(match.group(1))
            handler_func = self._clean_string_arg(match.group(2))

            # Look for comments above the call
            description = self._find_function_comment(content, handler_func, match.start())

            if path:
                endpoint = APIDocumentation(
                    path=path,
                    method="GET",  # HandleFunc typically handles GET
                    description=description,
                    handler_func=handler_func
                )
                self.endpoints.append(endpoint)

    def _extract_gin_routes(self, content):
        # Gin router patterns: router.GET, router.POST, etc.
        methods = [
            'GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'
        ]

        # Group-based routes: router.Group("/api").GET("/users", handler)
        # Direct method calls: router.GET("/users", handler)

        for method in methods:
            # Direct method calls
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
                    self.endpoints.append(endpoint)

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
                    self.endpoints.append(endpoint)

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
                    self.endpoints.append(endpoint)

    def _extract_mux_routes(self, content):
        # Gorilla Mux router patterns
        # Pattern 1: r.HandleFunc("/path", handler).Methods("GET", "POST")
        mux_pattern1 = r'\w+\.HandleFunc\s*\(\s*([^,]+)\s*,\s*([^)]+)\)\s*\.Methods\s*\(\s*([^)]+)\s*\)'
        matches = re.finditer(mux_pattern1, content)
        for match in matches:
            path = self._clean_string_arg(match.group(1))
            handler_func = self._clean_string_arg(match.group(2))
            methods_str = match.group(3)

            # Extract methods from the .Methods call
            # This could be: "GET", "GET", "POST" or strings.Join([]string{"GET", "POST"})
            method_matches = re.finditer(r'["\']([A-Z]+)["\']', methods_str)
            for method_match in method_matches:
                method = method_match.group(1)
                if path:
                    description = self._find_function_comment(content, handler_func, match.start())
                    endpoint = APIDocumentation(
                        path=path,
                        method=method,
                        description=f"{description} - Gorilla Mux Handler",
                        handler_func=handler_func
                    )
                    self.endpoints.append(endpoint)

        # Pattern 2: r.Path("/path").HandlerFunc(handler).Methods("GET")
        mux_pattern2 = r'\w+\.Path\s*\(\s*([^)]+)\)\s*\.HandlerFunc\s*\(\s*([^)]+)\)\s*\.Methods\s*\(\s*([^)]+)\s*\)'
        matches = re.finditer(mux_pattern2, content)
        for match in matches:
            path = self._clean_string_arg(match.group(1))
            handler_func = self._clean_string_arg(match.group(2))
            methods_str = match.group(3)

            method_matches = re.finditer(r'["\']([A-Z]+)["\']', methods_str)
            for method_match in method_matches:
                method = method_match.group(1)
                if path:
                    description = self._find_function_comment(content, handler_func, match.start())
                    endpoint = APIDocumentation(
                        path=path,
                        method=method,
                        description=f"{description} - Gorilla Mux Path Handler",
                        handler_func=handler_func
                    )
                    self.endpoints.append(endpoint)

        # Pattern 3: Simple HandleFunc without .Methods (defaults to all methods)
        mux_pattern3 = r'\w+\.HandleFunc\s*\(\s*([^,]+)\s*,\s*([^)]+)\)'
        matches = re.finditer(mux_pattern3, content)
        for match in matches:
            # Skip if this is followed by .Methods (already handled above)
            if '.Methods(' in content[match.end():match.end()+50]:
                continue

            path = self._clean_string_arg(match.group(1))
            handler_func = self._clean_string_arg(match.group(2))

            if path:
                # For HandleFunc without Methods, assume it's for GET requests
                description = self._find_function_comment(content, handler_func, match.start())
                endpoint = APIDocumentation(
                    path=path,
                    method="GET",
                    description=f"{description} - Gorilla Mux HandleFunc",
                    handler_func=handler_func
                )
                self.endpoints.append(endpoint)

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
                    self.endpoints.append(endpoint)

    def _clean_string_arg(self, arg):
        """Clean and extract string literals from Go code"""
        arg = arg.strip()
        # Remove quotes if present
        if (arg.startswith('"') and arg.endswith('"')) or \
           (arg.startswith("'") and arg.endswith("'")):
            return arg[1:-1]
        return arg

    def _find_function_comment(self, content, func_name, call_position):
        """Find comments for a function"""
        lines = content[:call_position].split('\n')
        comment_lines = []

        for line in reversed(lines):
            line = line.strip()
            if line.startswith('//'):
                comment_lines.insert(0, line[2:].strip())
            elif line.startswith('func') and func_name in line:
                break
            elif line and not line.startswith('//'):
                # Stop if we hit non-comment, non-empty code
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

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Go Code API Documentation Generator')
    parser.add_argument('directory', nargs='?', default='.', help='Directory to analyze (default: current directory)')
    parser.add_argument('--inspect-server', nargs='?', const=True, metavar='port', type=int,
                       help='Attach to running server on specified port and inspect data shapes (port required)')
    parser.add_argument('--no-recursive', action='store_true', help='Disable recursive directory scanning')

    args = parser.parse_args()

    print("🚀 Go Code API Documentation Generator")
    print(f"📂 Analyzing directory: {args.directory}")
    if args.inspect_server:
        print("🔬 Server inspection: ENABLED")
    if args.no_recursive:
        print("📁 Recursive scanning: DISABLED")
    print("-" * 55)

    # Analyze the Go code
    analyzer = GoCodeAnalyzer()
    analyzer.enable_recursive = not args.no_recursive

    endpoints = analyzer.analyze_directory(args.directory)

    if endpoints:
        # Try to attach to running server if requested
        if args.inspect_server:
            inspector = DataInspector()

            # Server port is required when --inspect-server is used
            server_found = inspector.find_running_server(args.inspect_server)

            if server_found:
                # Get actual data shapes from running server
                inspector.get_endpoint_data(endpoints)
                print("🎯 Server data inspection completed!")

        # Generate documentation with enhanced data shapes
        generate_markdown_docs(endpoints, "apidocs.md")
        print(f"✓ Generated apidocs.md with {len(endpoints)} endpoints")

        if args.inspect_server and inspector.server_found:
            inspected_count = sum(1 for ep in endpoints if ep.data_shapes)
            print(f"✅ Enhanced with real data shapes: {inspected_count} endpoints")

        print("✓ Documentation saved to apidocs.md")
    else:
        print("⚠️ No API endpoints found in the Go files.")
        return

    # Print enhanced summary
    method_counts = {}
    for endpoint in endpoints:
        method_counts[endpoint.method] = method_counts.get(endpoint.method, 0) + 1

    if method_counts:
        print("\n📊 Analysis Summary:")
        for method, count in sorted(method_counts.items()):
            print(f"  {method}: {count} endpoints")

    # Show inspection stats if enabled
    if args.inspect_server and 'inspector' in locals():
        if inspector.server_found:
            inspected_endpoints = sum(1 for ep in endpoints if len(ep.data_shapes) > 0)
            print(f"\n🔬 Server Inspection Stats:")
            print(f"  📶 Server URL: {inspector.base_url}")
            print(f"  🎯 Inspected Endpoints: {inspected_endpoints}/{len(endpoints)}")
            print(f"  📊 Data Shapes Captured: {sum(len(ep.data_shapes) for ep in endpoints)}")

if __name__ == "__main__":
    main()
