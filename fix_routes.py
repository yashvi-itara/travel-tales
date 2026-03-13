import sys

file_path = r'c:\Users\yashvi.patel\Desktop\Travel Tales\app\blueprints\main\routes.py'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
in_seed_data = False
indent_next = False
extra_indent = "    "

for line in lines:
    if "def seed_data():" in line:
        in_seed_data = True
        new_lines.append(line)
        continue
    
    if in_seed_data:
        if "return " in line and "jsonify" in line and "Seeded successfully" in line:
            new_lines.append(extra_indent + line)
            new_lines.append(extra_indent[4:] + "    except Exception as e:\n")
            new_lines.append(extra_indent[4:] + "        import traceback\n")
            new_lines.append(extra_indent[4:] + "        db.session.rollback()\n")
            new_lines.append(extra_indent[4:] + "        return jsonify({\"status\": \"error\", \"message\": str(e), \"traceback\": traceback.format_exc()}), 500\n")
            in_seed_data = False
            continue
        
        if line.strip().startswith("@") and "route" in line:
            # We reached the next route before finding the return? 
            # This shouldn't happen if we are precise.
            pass
            
        new_lines.append(extra_indent + line)
    else:
        new_lines.append(line)

# This script is a bit risky if I don't handle the existing try/except correctly.
# Let's just write the whole function content to a separate file and then cat it in.
