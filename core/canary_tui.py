#!/usr/bin/env python3
"""
Smart Canary Protocol - Terminal User Interface
Interactive menu system for all canary operations
"""

import curses
import subprocess
import sys
import os
from datetime import datetime
import time
from typing import List, Tuple, Optional

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from functions.utils import log_error
except ImportError:
    # Fallback for when running from different directory
    sys.path.append(os.path.join(os.path.dirname(__file__), 'functions'))
    from utils import log_error

class CanaryTUI:
    def __init__(self):
        self.menu_items = [
            # Core Functions
            ("🔄 Run Protocol", "run", "Execute main canary protocol"),
            ("🚨 Emergency Analysis", "emergency", "Run immediate threat assessment"),
            ("🧪 Test System", "test", "Test system functionality"),
            
            # System Management
            ("📈 System Status", "status", "Check system health"),
            ("⚙️  Configuration", "config", "Edit system configuration"),
            ("📋 View Logs", "logs", "Show recent system logs"),
            ("🚀 System Setup", "setup", "Run complete system setup"),
            ("🔧 Fix Cron Jobs", "cron-reset", "Reset and fix duplicate cron jobs"),
            ("🗑️  Uninstall System", "uninstall", "Remove Smart Canary Protocol"),
            
            # Data & Backup Management
            ("🔒 Backup System", "backup", "Backup all learning data"),
            ("🔄 Restore Data", "restore", "Restore system data from backup"),
            ("✅ Backup Verification", "verify", "Verify backup integrity"),
            ("📦 Data Archival", "archive", "Archive old data"),
            ("🔧 Database Migrations", "migrate", "Manage database schema"),
            
            # Learning & Feedback
            ("🧠 Learning Dashboard", "dashboard", "View learning analytics"),
            ("📝 Digest Feedback", "feedback", "Provide feedback on digests"),
            ("📰 Article Feedback", "articles", "Rate individual articles"),
            ("📊 Feedback Summary", "feedback-summary", "View all feedback statistics"),
            ("🗑️  Clear Feedback", "feedback-clear", "Clear feedback data"),
            
            # Advanced Features
            ("🧪 A/B Testing", "ab-test", "Run A/B testing framework"),
        ]
        self.selected = 0
        self.scroll_offset = 0
        self.running = True

    def draw_header(self, stdscr):
        """Draw the application header"""
        height, width = stdscr.getmaxyx()
        
        # Title
        title = "🐦 Smart Canary Protocol - Interactive Control Panel"
        stdscr.addstr(0, (width - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(1))
        
        # Subtitle
        subtitle = "Navigate with ↑↓ arrows, Enter to select, 'q' to quit"
        stdscr.addstr(1, (width - len(subtitle)) // 2, subtitle, curses.color_pair(2))
        
        # Separator
        stdscr.addstr(2, 0, "─" * width, curses.color_pair(2))

    def draw_menu(self, stdscr):
        """Draw the main menu with scrolling support"""
        height, width = stdscr.getmaxyx()
        start_y = 4
        menu_height = height - 6  # Reserve space for header and footer
        items_per_screen = menu_height // 2  # Each item takes 2 lines
        
        # Calculate visible range
        visible_start = self.scroll_offset
        visible_end = min(visible_start + items_per_screen, len(self.menu_items))
        
        # Draw visible menu items
        for i in range(visible_start, visible_end):
            display_index = i - visible_start
            y = start_y + display_index * 2
            
            name, command, description = self.menu_items[i]
            
            # Highlight selected item
            if i == self.selected:
                stdscr.addstr(y, 2, f"► {name}", curses.A_REVERSE | curses.A_BOLD)
                # Show description for selected item
                if len(description) < width - 6:
                    stdscr.addstr(y + 1, 4, description, curses.color_pair(3))
            else:
                stdscr.addstr(y, 4, name, curses.A_NORMAL)
        
        # Show scroll indicators if needed
        if len(self.menu_items) > items_per_screen:
            # Show up arrow if not at top
            if self.scroll_offset > 0:
                stdscr.addstr(start_y - 1, width - 3, "↑", curses.color_pair(2))
            
            # Show down arrow if not at bottom
            if visible_end < len(self.menu_items):
                stdscr.addstr(height - 4, width - 3, "↓", curses.color_pair(2))
            
            # Show scroll position
            scroll_info = f"({self.selected + 1}/{len(self.menu_items)})"
            stdscr.addstr(height - 3, width - len(scroll_info) - 1, scroll_info, curses.color_pair(2))

    def draw_footer(self, stdscr):
        """Draw the footer with controls"""
        height, width = stdscr.getmaxyx()
        footer_y = height - 2
        
        controls = "Controls: ↑↓ Navigate | Enter Select | q Quit | h Help"
        stdscr.addstr(footer_y, (width - len(controls)) // 2, controls, curses.color_pair(2))

    def show_help(self, stdscr):
        """Show help dialog"""
        height, width = stdscr.getmaxyx()
        
        help_text = [
            "Smart Canary Protocol - Help",
            "=" * 30,
            "",
            "Navigation:",
            "  ↑/k     - Move up",
            "  ↓/j     - Move down", 
            "  Enter   - Execute selected command",
            "  q       - Quit application",
            "  h       - Show this help",
            "",
            "Features:",
            "  • Interactive menu for all canary operations",
            "  • Real-time command execution",
            "  • System status monitoring",
            "  • Backup and maintenance tools",
            "",
            "Press any key to continue..."
        ]
        
        # Clear screen and show help
        stdscr.clear()
        for i, line in enumerate(help_text):
            if i < height - 1:
                stdscr.addstr(i, 2, line[:width-4])
        
        stdscr.refresh()
        stdscr.getch()

    def execute_command(self, stdscr, command: str) -> bool:
        """Execute the selected command"""
        try:
            # Check if it's a canary command (most commands now use ./canary interface)
            canary_commands = ["status", "config", "logs", "restore", "feedback-summary", "feedback-clear", 
                             "emergency", "test", "setup", "cron-reset", "uninstall", "backup", "verify", 
                             "dashboard", "feedback", "articles", "archive", "migrate", "ab-test", "run"]
            
            if command in canary_commands:
                # Use the unified canary script
                result = subprocess.run(["./canary", command], cwd="..", capture_output=True, text=True)
            else:
                # Direct script execution for commands not yet integrated
                result = subprocess.run(command.split(), cwd="..", capture_output=True, text=True)
            
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)

    def show_feedback_summary(self, stdscr) -> bool:
        """Show feedback summary"""
        try:
            curses.endwin()
            
            # Use the unified canary command
            subprocess.run(["./canary", "feedback-summary"], cwd="..")
            
            input("\nPress Enter to continue...")
            
            stdscr = curses.initscr()
            curses.noecho()
            curses.cbreak()
            stdscr.keypad(True)
            
        except Exception as e:
            print(f"Error: {e}")
            input("Press Enter to continue...")
        
        return True

    def show_feedback_clear(self, stdscr) -> bool:
        """Show feedback clear options"""
        try:
            curses.endwin()
            
            # Use the unified canary command which handles the interactive menu
            subprocess.run(["./canary", "feedback-clear"], cwd="..")
            
            input("Press Enter to continue...")
            
            stdscr = curses.initscr()
            curses.noecho()
            curses.cbreak()
            stdscr.keypad(True)
            
        except Exception as e:
            print(f"Error: {e}")
            input("Press Enter to continue...")
        
        return True

    def show_logs(self, stdscr) -> bool:
        """Show recent logs"""
        try:
            curses.endwin()
            
            print("📋 Smart Canary Protocol - Recent Logs")
            print("=" * 38)
            print()
            
            # Show recent error logs
            print("🔍 Recent Error Log (last 10 entries):")
            if os.path.exists("logs/error.log"):
                subprocess.run(["tail", "-10", "logs/error.log"])
            else:
                print("No error log found.")
            
            print("\n📊 Recent Activity Log (last 10 entries):")
            if os.path.exists("logs/canary.log"):
                subprocess.run(["tail", "-10", "logs/canary.log"])
            else:
                print("No activity log found.")
            
            input("\nPress Enter to continue...")
            
            stdscr = curses.initscr()
            curses.noecho()
            curses.cbreak()
            stdscr.keypad(True)
            
        except Exception as e:
            print(f"Error: {e}")
            input("Press Enter to continue...")
        
        return True

    def show_status(self, stdscr) -> bool:
        """Show system status"""
        try:
            curses.endwin()
            
            print("📈 Smart Canary Protocol - System Status")
            print("=" * 40)
            print()
            
            # Check database
            if os.path.exists("data/canary_protocol.db"):
                size = os.path.getsize("data/canary_protocol.db")
                print(f"✅ Database: OK ({size/1024/1024:.1f} MB)")
            else:
                print("❌ Database: Not found")
            
            # Check configuration
            if os.path.exists("config/config_defaults.yaml"):
                print("✅ Configuration: OK")
            else:
                print("❌ Configuration: Missing")
            
            # Check logs directory
            if os.path.exists("logs/"):
                log_count = len([f for f in os.listdir("logs/") if f.endswith('.log')])
                print(f"✅ Logs: OK ({log_count} files)")
            else:
                print("❌ Logs: Directory missing")
            
            # Check Python dependencies
            try:
                import openai, yaml, feedparser
                print("✅ Dependencies: OK")
            except ImportError as e:
                print(f"❌ Dependencies: Missing {e}")
            
            input("\nPress Enter to continue...")
            
            stdscr = curses.initscr()
            curses.noecho()
            curses.cbreak()
            stdscr.keypad(True)
            
        except Exception as e:
            print(f"Error: {e}")
            input("Press Enter to continue...")
        
        return True

    def show_config(self, stdscr) -> bool:
        """Show configuration interface"""
        try:
            curses.endwin()
            
            print("⚙️  Smart Canary Protocol - Configuration")
            print("=" * 42)
            print()
            
            # Show current config file locations
            config_dir = "config"
            config_file = f"{config_dir}/config.yaml"
            env_file = f"{config_dir}/.env"
            
            print("📁 Configuration Files:")
            if os.path.exists(config_file):
                print(f"✅ Main config: {config_file}")
            else:
                print(f"❌ Main config: {config_file} (not found)")
            
            if os.path.exists(env_file):
                print(f"✅ Environment: {env_file}")
            else:
                print(f"❌ Environment: {env_file} (not found)")
            
            print()
            print("🔧 Configuration Options:")
            print("1. Edit main configuration (config.yaml)")
            print("2. Edit environment variables (.env)")
            print("3. Create example configuration")
            print("4. Validate current configuration")
            print("5. Return to main menu")
            print()
            
            try:
                choice = input("Select option (1-5): ").strip()
                
                if choice == "1":
                    if os.path.exists(config_file):
                        os.system(f"${EDITOR:-nano} {config_file}")
                    else:
                        print(f"❌ Config file not found: {config_file}")
                        input("Press Enter to continue...")
                elif choice == "2":
                    if os.path.exists(env_file):
                        os.system(f"${EDITOR:-nano} {env_file}")
                    else:
                        print(f"❌ Environment file not found: {env_file}")
                        input("Press Enter to continue...")
                elif choice == "3":
                    # Create example config using ConfigLoader
                    try:
                        sys.path.append(os.path.join(os.path.dirname(__file__), 'classes'))
                        from config_loader import ConfigLoader
                        config_loader = ConfigLoader()
                        if config_loader.create_example_user_config():
                            print("✅ Example configuration created!")
                        else:
                            print("❌ Failed to create example configuration")
                    except Exception as e:
                        print(f"❌ Error creating example config: {e}")
                    input("Press Enter to continue...")
                elif choice == "4":
                    # Validate configuration
                    try:
                        sys.path.append(os.path.join(os.path.dirname(__file__), 'classes'))
                        from config_loader import ConfigLoader
                        config_loader = ConfigLoader()
                        print("✅ Configuration loaded successfully!")
                        print(f"📊 Loaded {len(config_loader._config)} configuration sections")
                    except Exception as e:
                        print(f"❌ Configuration validation failed: {e}")
                    input("Press Enter to continue...")
                elif choice == "5":
                    pass  # Return to menu
                else:
                    print("❌ Invalid option")
                    input("Press Enter to continue...")
                    
            except EOFError:
                pass  # Handle non-interactive execution
            
            stdscr = curses.initscr()
            curses.noecho()
            curses.cbreak()
            stdscr.keypad(True)
            
        except Exception as e:
            print(f"Error: {e}")
            input("Press Enter to continue...")
        
        return True

    def show_restore(self, stdscr) -> bool:
        """Show restore interface using DataRestoreManager"""
        try:
            curses.endwin()
            
            # Import and use DataRestoreManager
            sys.path.append(os.path.join(os.path.dirname(__file__), 'classes'))
            from data_restore import DataRestoreManager
            
            restore_manager = DataRestoreManager()
            success = restore_manager.interactive_restore()
            
            if not success:
                input("Press Enter to continue...")
            
            stdscr = curses.initscr()
            curses.noecho()
            curses.cbreak()
            stdscr.keypad(True)
            
        except Exception as e:
            print(f"Error: {e}")
            input("Press Enter to continue...")
        
        return True

    def _update_scroll(self):
        """Update scroll offset to keep selected item visible"""
        height, width = curses.LINES, curses.COLS
        menu_height = height - 6
        items_per_screen = menu_height // 2
        
        # Scroll down if selected item is below visible area
        if self.selected >= self.scroll_offset + items_per_screen:
            self.scroll_offset = self.selected - items_per_screen + 1
        
        # Scroll up if selected item is above visible area
        elif self.selected < self.scroll_offset:
            self.scroll_offset = self.selected
        
        # Ensure scroll offset is within bounds
        max_scroll = max(0, len(self.menu_items) - items_per_screen)
        self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

    def run(self, stdscr):
        """Main application loop"""
        # Initialize colors
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Title
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Subtitle/controls
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Description
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)     # Error
        
        # Configure curses
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)
        stdscr.timeout(100)  # Non-blocking input
        
        while self.running:
            stdscr.clear()
            
            # Draw interface
            self.draw_header(stdscr)
            self.draw_menu(stdscr)
            self.draw_footer(stdscr)
            
            stdscr.refresh()
            
            # Handle input
            key = stdscr.getch()
            
            if key == ord('q') or key == ord('Q'):
                self.running = False
            elif key == ord('h') or key == ord('H'):
                self.show_help(stdscr)
            elif key == curses.KEY_UP or key == ord('k'):
                self.selected = (self.selected - 1) % len(self.menu_items)
                self._update_scroll()
            elif key == curses.KEY_DOWN or key == ord('j'):
                self.selected = (self.selected + 1) % len(self.menu_items)
                self._update_scroll()
            elif key == ord('\n') or key == curses.KEY_ENTER or key == 10:
                _, command, _ = self.menu_items[self.selected]
                if not self.execute_command(stdscr, command):
                    self.running = False

def main():
    """Main entry point"""
    try:
        tui = CanaryTUI()
        curses.wrapper(tui.run)
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
