

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="OCR Translate Entry Point")
    parser.add_argument("--mode", choices=["cli", "gui"], default="gui", help="Select mode: cli or gui")
    args = parser.parse_args()

    if args.mode == "cli":
        print("CLI mode selected. (To be implemented)")
        # run_cli()
    elif args.mode == "gui":
        print("Launching GUI...")
        from .ui import main_window
        main_window.run_gui()  # You need to define run_gui() inside main_window.py