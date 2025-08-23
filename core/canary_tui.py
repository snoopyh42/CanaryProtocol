#!/usr/bin/env python3
"""
Smart Canary Protocol - Terminal User Interface
Interactive menu system for all canary operations
"""

import curses
import subprocess
import sys
import os
from typing import List, Tuple, Optional

class CanaryTUI:
    def __init__(self):
        self.menu_items = [
            ("🚀 System Setup", "scripts/setup_complete_smart_system.sh", "Run complete system setup"),
            ("🧠 Learning Dashboard", "scripts/learning_dashboard.sh", "View learning analytics"),
            ("📝 Digest Feedback", "python3 core/smart_feedback.py", "Provide feedback on digests"),
            ("📰 Article Feedback", "python3 core/individual_feedback.py", "Rate individual articles"),
            ("📊 Feedback Summary", "feedback-summary", "View all feedback statistics"),
            ("🗑️  Clear Feedback", "feedback-clear", "Clear feedback data"),
            ("🔍 A/B Testing", "python3 core/ab_testing.py", "Run A/B tests"),
            ("🚨 Emergency Analysis", "scripts/emergency_analysis.sh", "Run emergency analysis"),
            ("🧪 Test System", "python3 core/canary_protocol.py --test", "Test system functionality"),
            ("💾 Create Backup", "scripts/backup_learning_data.sh", "Backup system data"),
            ("📋 View Logs", "logs", "View recent system logs"),
            ("📈 System Status", "status", "Check system health"),
            ("🔧 Database Migrations", "python3 core/database_migrations.py", "Manage database schema"),
            ("📦 Data Archival", "python3 core/data_archival.py", "Archive old data"),
            ("✅ Backup Verification", "python3 core/backup_verification.py", "Verify backup integrity"),
        ]
        self.selected = 0
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
        """Draw the main menu"""
        height, width = stdscr.getmaxyx()
        start_y = 4
        
        for i, (name, command, description) in enumerate(self.menu_items):
            y = start_y + i * 2
            
            if y >= height - 3:  # Leave space for footer
                break
                
            # Highlight selected item
            if i == self.selected:
                stdscr.addstr(y, 2, f"► {name}", curses.A_REVERSE | curses.A_BOLD)
                # Show description for selected item
                if len(description) < width - 6:
                    stdscr.addstr(y + 1, 4, description, curses.color_pair(3))
            else:
                stdscr.addstr(y, 4, name, curses.A_NORMAL)

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
        """Execute a command and show results"""
        height, width = stdscr.getmaxyx()
        
        # Handle special commands
        if command == "feedback-summary":
            return self.show_feedback_summary(stdscr)
        elif command == "feedback-clear":
            return self.show_feedback_clear(stdscr)
        elif command == "logs":
            return self.show_logs(stdscr)
        elif command == "status":
            return self.show_status(stdscr)
        
        # Execute regular shell command
        try:
            # Temporarily exit curses mode completely
            curses.endwin()
            
            # Clear terminal and show what we're executing
            os.system('clear')
            print(f"🐦 Smart Canary Protocol")
            print(f"Executing: {command}")
            print("=" * 50)
            print()
            
            # Execute command with full terminal control
            result = subprocess.run(command, shell=True, cwd=os.getcwd())
            
            # Show completion status and wait for user
            print()
            print("=" * 50)
            if result.returncode == 0:
                print("✅ Command completed successfully!")
            else:
                print(f"❌ Command failed with exit code: {result.returncode}")
            
            print()
            input("Press Enter to return to menu...")
            
            # Reinitialize curses completely
            stdscr = curses.initscr()
            curses.start_color()
            curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
            curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
            curses.noecho()
            curses.cbreak()
            stdscr.keypad(True)
            stdscr.timeout(100)
            
        except Exception as e:
            # If something goes wrong, try to recover
            try:
                curses.endwin()
                print(f"❌ Error executing command: {str(e)}")
                input("Press Enter to return to menu...")
                stdscr = curses.initscr()
                curses.start_color()
                curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
                curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
                curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
                curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
                curses.noecho()
                curses.cbreak()
                stdscr.keypad(True)
                stdscr.timeout(100)
            except:
                return False
        
        return True

    def show_feedback_summary(self, stdscr) -> bool:
        """Show feedback summary"""
        try:
            curses.endwin()
            
            print("📊 Feedback Summary:")
            print("=" * 20)
            print()
            print("📝 Digest-level feedback:")
            subprocess.run(["python3", "core/smart_feedback.py", "--summary"])
            print()
            print("📰 Individual article feedback:")
            subprocess.run(["python3", "core/individual_feedback.py", "--summary"])
            
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
            
            print("🗑️  Clear Feedback Data")
            print("=" * 23)
            print()
            print("Choose what to clear:")
            print("1) Digest-level feedback only")
            print("2) Individual article feedback only")
            print("3) ALL feedback data")
            print("4) Cancel")
            print()
            
            choice = input("Enter choice (1-4): ")
            
            if choice == "1":
                subprocess.run(["python3", "core/smart_feedback.py", "--clear"])
            elif choice == "2":
                subprocess.run(["python3", "core/individual_feedback.py", "--clear"])
            elif choice == "3":
                subprocess.run(["python3", "core/smart_feedback.py", "--clear"])
                subprocess.run(["python3", "core/individual_feedback.py", "--clear"])
            elif choice == "4":
                print("Cancelled.")
            else:
                print("Invalid choice.")
            
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
            elif key == curses.KEY_DOWN or key == ord('j'):
                self.selected = (self.selected + 1) % len(self.menu_items)
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
