"""
Data Tools - Consolidated data processing and analytics for AI agents
Provides unified data operations, visualization, and analysis capabilities.
"""
from typing import Any, Dict, List
import os
import tempfile
import json

def data_processor(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Universal data processor - replaces load_csv, describe_data, plot_chart, query_data, export_data
    
    Args:
        action (str): Action to perform - 'load', 'describe', 'plot', 'query', 'export', 'transform', 'analyze'
        file (str): Data file path (for load, export actions)
        data (dict/list): Data to process (for in-memory operations)
        output_path (str): Output file path (for export, plot actions)
        plot_type (str): Chart type - 'bar', 'line', 'scatter', 'pie', 'histogram' (for plot action)
        x_column (str): X-axis column (for plot action)
        y_column (str): Y-axis column (for plot action)
        query (str): SQL-like query string (for query action)
        format (str): Export format - 'csv', 'json', 'excel' (for export action)
        
    Returns:
        Dict with processing result
    """
    if not args or "action" not in args:
        return {"success": False, "result": None, "error": "Missing required argument: action"}
    
    action = args["action"]
    
    try:
        if action == "load":
            return _load_data_impl(args)
        elif action == "describe":
            return _describe_data_impl(args)
        elif action == "plot":
            return _plot_chart_impl(args)
        elif action == "query":
            return _query_data_impl(args)
        elif action == "export":
            return _export_data_impl(args)
        elif action == "transform":
            return _transform_data_impl(args)
        elif action == "analyze":
            return _analyze_data_impl(args)
        else:
            return {
                "success": False,
                "result": None,
                "error": f"Unknown action: {action}. Use: load, describe, plot, query, export, transform, analyze"
            }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Data processing failed: {str(e)}"}

# Data Processor Implementation Helpers
def _load_data_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Load data from file implementation"""
    try:
        file_path = args.get("file")
        if not file_path:
            return {"success": False, "result": None, "error": "Missing required argument: file"}
        
        if not os.path.exists(file_path):
            return {"success": False, "result": None, "error": f"Data file not found: {file_path}"}
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # Load based on file type
        if file_ext == ".csv":
            return _load_csv_impl(args)
        elif file_ext == ".json":
            return _load_json_impl(args)
        elif file_ext in [".xlsx", ".xls"]:
            return _load_excel_impl(args)
        else:
            return {"success": False, "result": None, "error": f"Unsupported file format: {file_ext}"}
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to load data: {str(e)}"}

def _load_csv_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Load CSV file implementation"""
    try:
        file_path = args["file"]
        delimiter = args.get("delimiter", ",")
        has_header = args.get("has_header", True)
        max_rows = args.get("max_rows", None)
        
        # Try pandas first (most powerful)
        try:
            import pandas as pd
            
            df = pd.read_csv(file_path, delimiter=delimiter, nrows=max_rows)
            
            # Get basic statistics
            numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
            stats = {}
            if numeric_columns:
                stats = df[numeric_columns].describe().to_dict()
            
            return {
                "success": True,
                "result": {
                    "file_path": file_path,
                    "rows": len(df),
                    "columns": len(df.columns),
                    "column_names": list(df.columns),
                    "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
                    "sample_data": df.head(5).to_dict('records'),
                    "statistics": stats,
                    "memory_usage_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
                    "method": "pandas_csv"
                },
                "error": None
            }
        
        except ImportError:
            # Fallback to built-in csv module
            import csv
            
            data = []
            column_names = []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                if has_header:
                    reader = csv.DictReader(f, delimiter=delimiter)
                    column_names = reader.fieldnames
                    for i, row in enumerate(reader):
                        if max_rows and i >= max_rows:
                            break
                        data.append(row)
                else:
                    reader = csv.reader(f, delimiter=delimiter)
                    for i, row in enumerate(reader):
                        if max_rows and i >= max_rows:
                            break
                        data.append(row)
                    column_names = [f"col_{i}" for i in range(len(data[0]) if data else 0)]
            
            return {
                "success": True,
                "result": {
                    "file_path": file_path,
                    "rows": len(data),
                    "columns": len(column_names),
                    "column_names": column_names,
                    "sample_data": data[:5],
                    "method": "csv_builtin"
                },
                "error": None
            }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to load CSV: {str(e)}"}

def _load_json_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Load JSON file implementation"""
    try:
        file_path = args["file"]
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Analyze JSON structure
        if isinstance(data, list):
            rows = len(data)
            columns = len(data[0].keys()) if data and isinstance(data[0], dict) else 0
            column_names = list(data[0].keys()) if data and isinstance(data[0], dict) else []
            sample_data = data[:5]
        elif isinstance(data, dict):
            rows = 1
            columns = len(data.keys())
            column_names = list(data.keys())
            sample_data = [data]
        else:
            rows = 1
            columns = 1
            column_names = ["value"]
            sample_data = [{"value": data}]
        
        return {
            "success": True,
            "result": {
                "file_path": file_path,
                "rows": rows,
                "columns": columns,
                "column_names": column_names,
                "sample_data": sample_data,
                "data_type": type(data).__name__,
                "method": "json_builtin"
            },
            "error": None
        }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to load JSON: {str(e)}"}

def _load_excel_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Load Excel file implementation"""
    try:
        file_path = args["file"]
        sheet_name = args.get("sheet_name", 0)  # First sheet by default
        
        try:
            import pandas as pd
            
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            return {
                "success": True,
                "result": {
                    "file_path": file_path,
                    "sheet_name": sheet_name,
                    "rows": len(df),
                    "columns": len(df.columns),
                    "column_names": list(df.columns),
                    "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
                    "sample_data": df.head(5).to_dict('records'),
                    "method": "pandas_excel"
                },
                "error": None
            }
        
        except ImportError:
            return {"success": False, "result": None, "error": "Excel support requires pandas and openpyxl (pip install pandas openpyxl)"}
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to load Excel: {str(e)}"}

def _describe_data_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Describe data implementation"""
    try:
        # Get data from file or direct input
        if args.get("file"):
            load_result = _load_data_impl(args)
            if not load_result["success"]:
                return load_result
            data_info = load_result["result"]
        else:
            data = args.get("data")
            if not data:
                return {"success": False, "result": None, "error": "Missing data source: provide 'file' or 'data'"}
            
            # Analyze provided data
            if isinstance(data, list):
                rows = len(data)
                columns = len(data[0].keys()) if data and isinstance(data[0], dict) else 0
                column_names = list(data[0].keys()) if data and isinstance(data[0], dict) else []
            else:
                rows = 1
                columns = len(data.keys()) if isinstance(data, dict) else 1
                column_names = list(data.keys()) if isinstance(data, dict) else ["value"]
            
            data_info = {
                "rows": rows,
                "columns": columns,
                "column_names": column_names,
                "sample_data": data[:5] if isinstance(data, list) else [data]
            }
        
        # Generate description
        description = {
            "overview": {
                "total_rows": data_info["rows"],
                "total_columns": data_info["columns"],
                "column_names": data_info["column_names"]
            },
            "data_quality": {
                "has_data": data_info["rows"] > 0,
                "has_columns": data_info["columns"] > 0,
                "sample_available": len(data_info.get("sample_data", [])) > 0
            }
        }
        
        # Add statistics if available
        if "statistics" in data_info:
            description["statistics"] = data_info["statistics"]
        
        return {
            "success": True,
            "result": {
                "description": description,
                "sample_data": data_info.get("sample_data", []),
                "method": "data_description"
            },
            "error": None
        }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to describe data: {str(e)}"}

def _plot_chart_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Plot chart implementation"""
    try:
        plot_type = args.get("plot_type", "bar")
        output_path = args.get("output_path")
        
        if not output_path:
            output_path = os.path.join(tempfile.gettempdir(), f"chart_{plot_type}.png")
        
        # Try matplotlib for plotting
        try:
            import matplotlib.pyplot as plt
            import pandas as pd
            
            # Get data
            if args.get("file"):
                load_result = _load_csv_impl(args)
                if not load_result["success"]:
                    return load_result
                
                # Load data into pandas for plotting
                df = pd.read_csv(args["file"])
            else:
                data = args.get("data")
                if not data:
                    return {"success": False, "result": None, "error": "Missing data source: provide 'file' or 'data'"}
                df = pd.DataFrame(data)
            
            # Get plot parameters
            x_column = args.get("x_column")
            y_column = args.get("y_column")
            title = args.get("title", f"{plot_type.title()} Chart")
            
            # Create plot
            plt.figure(figsize=(10, 6))
            
            if plot_type == "bar":
                if x_column and y_column:
                    plt.bar(df[x_column], df[y_column])
                    plt.xlabel(x_column)
                    plt.ylabel(y_column)
                else:
                    # Plot first numeric column
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    if len(numeric_cols) > 0:
                        df[numeric_cols[0]].plot(kind='bar')
            
            elif plot_type == "line":
                if x_column and y_column:
                    plt.plot(df[x_column], df[y_column])
                    plt.xlabel(x_column)
                    plt.ylabel(y_column)
                else:
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    if len(numeric_cols) > 0:
                        df[numeric_cols[0]].plot(kind='line')
            
            elif plot_type == "scatter":
                if x_column and y_column:
                    plt.scatter(df[x_column], df[y_column])
                    plt.xlabel(x_column)
                    plt.ylabel(y_column)
            
            elif plot_type == "histogram":
                column = y_column or x_column
                if column:
                    plt.hist(df[column], bins=20)
                    plt.xlabel(column)
                    plt.ylabel("Frequency")
            
            elif plot_type == "pie":
                if x_column and y_column:
                    plt.pie(df[y_column], labels=df[x_column], autopct='%1.1f%%')
            
            plt.title(title)
            plt.tight_layout()
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
            
            return {
                "success": True,
                "result": {
                    "plot_type": plot_type,
                    "output_path": output_path,
                    "title": title,
                    "x_column": x_column,
                    "y_column": y_column,
                    "file_size": file_size,
                    "method": "matplotlib"
                },
                "error": None
            }
        
        except ImportError:
            return {"success": False, "result": None, "error": "Plotting requires matplotlib and pandas (pip install matplotlib pandas)"}
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to create plot: {str(e)}"}

def _query_data_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Query data implementation"""
    try:
        query = args.get("query")
        if not query:
            return {"success": False, "result": None, "error": "Missing required argument: query"}
        
        # Try pandas with SQL-like queries
        try:
            import pandas as pd
            
            # Load data
            if args.get("file"):
                df = pd.read_csv(args["file"])
            else:
                data = args.get("data")
                if not data:
                    return {"success": False, "result": None, "error": "Missing data source"}
                df = pd.DataFrame(data)
            
            # Simple query parsing (basic implementation)
            query_lower = query.lower().strip()
            
            if query_lower.startswith("select"):
                # Basic SELECT implementation
                if "where" in query_lower:
                    # Very basic WHERE clause parsing
                    return {"success": False, "result": None, "error": "Complex SQL queries not yet supported. Use pandas operations."}
                else:
                    # Simple SELECT *
                    if "select *" in query_lower:
                        result_df = df
                    else:
                        return {"success": False, "result": None, "error": "Only 'SELECT *' queries supported currently"}
            
            elif query_lower.startswith("count"):
                result_df = pd.DataFrame({"count": [len(df)]})
            
            else:
                return {"success": False, "result": None, "error": f"Unsupported query type. Query: {query}"}
            
            return {
                "success": True,
                "result": {
                    "query": query,
                    "rows_returned": len(result_df),
                    "columns": list(result_df.columns),
                    "data": result_df.to_dict('records'),
                    "method": "pandas_query"
                },
                "error": None
            }
        
        except ImportError:
            return {"success": False, "result": None, "error": "Data querying requires pandas (pip install pandas)"}
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to query data: {str(e)}"}

def _export_data_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Export data implementation"""
    try:
        output_path = args.get("output_path")
        format_type = args.get("format", "csv")
        
        if not output_path:
            output_path = os.path.join(tempfile.gettempdir(), f"export.{format_type}")
        
        # Get data
        if args.get("file"):
            # Load and re-export (format conversion)
            load_result = _load_data_impl(args)
            if not load_result["success"]:
                return load_result
            
            # Load original data
            import pandas as pd
            df = pd.read_csv(args["file"])
        else:
            data = args.get("data")
            if not data:
                return {"success": False, "result": None, "error": "Missing data source"}
            
            import pandas as pd
            df = pd.DataFrame(data)
        
        # Export based on format
        if format_type == "csv":
            df.to_csv(output_path, index=False)
        elif format_type == "json":
            df.to_json(output_path, orient='records', indent=2)
        elif format_type == "excel":
            df.to_excel(output_path, index=False)
        else:
            return {"success": False, "result": None, "error": f"Unsupported export format: {format_type}"}
        
        file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
        
        return {
            "success": True,
            "result": {
                "output_path": output_path,
                "format": format_type,
                "rows_exported": len(df),
                "columns_exported": len(df.columns),
                "file_size": file_size,
                "method": "pandas_export"
            },
            "error": None
        }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to export data: {str(e)}"}

def _transform_data_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Transform data implementation"""
    try:
        transform_type = args.get("transform_type", "filter")
        
        # Basic data transformations
        return {
            "success": False,
            "result": None,
            "error": "Data transformations not yet implemented. Use pandas directly for complex operations."
        }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to transform data: {str(e)}"}

def _analyze_data_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze data implementation"""
    try:
        # Get data
        if args.get("file"):
            load_result = _load_data_impl(args)
            if not load_result["success"]:
                return load_result
            data_info = load_result["result"]
        else:
            data = args.get("data")
            if not data:
                return {"success": False, "result": None, "error": "Missing data source"}
            
            # Basic analysis of provided data
            if isinstance(data, list) and data:
                rows = len(data)
                if isinstance(data[0], dict):
                    columns = len(data[0].keys())
                    column_names = list(data[0].keys())
                else:
                    columns = 1
                    column_names = ["value"]
            else:
                rows = 1
                columns = 1
                column_names = ["value"]
            
            data_info = {
                "rows": rows,
                "columns": columns,
                "column_names": column_names
            }
        
        # Generate analysis
        analysis = {
            "data_shape": {
                "rows": data_info["rows"],
                "columns": data_info["columns"]
            },
            "data_quality": {
                "completeness": "unknown",  # Would need null checking
                "consistency": "unknown",   # Would need validation rules
                "accuracy": "unknown"      # Would need reference data
            },
            "insights": [
                f"Dataset contains {data_info['rows']} rows and {data_info['columns']} columns",
                f"Columns: {', '.join(data_info['column_names'][:5])}{'...' if len(data_info['column_names']) > 5 else ''}"
            ]
        }
        
        return {
            "success": True,
            "result": {
                "analysis": analysis,
                "method": "basic_analysis"
            },
            "error": None
        }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to analyze data: {str(e)}"}

# Legacy function aliases for backward compatibility
def load_csv(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use data_processor instead"""
    return data_processor(args={"action": "load", **(args or {})})

def describe_data(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use data_processor instead"""
    return data_processor(args={"action": "describe", **(args or {})})

def plot_chart(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use data_processor instead"""
    return data_processor(args={"action": "plot", **(args or {})})

def query_data(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use data_processor instead"""
    return data_processor(args={"action": "query", **(args or {})})

def export_data(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use data_processor instead"""
    return data_processor(args={"action": "export", **(args or {})})
