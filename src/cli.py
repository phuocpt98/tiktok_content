"""Tạp Hóa Pel Pel - TikTok Content CLI."""
import sys
import os
import json
import importlib
from pathlib import Path

# Fix Windows Unicode encoding
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

app = typer.Typer(help="Tạp Hóa Pel Pel - TikTok Content Creator")
console = Console()

# Helper to import modules with hyphens in filename
def _import(module_name: str):
    """Import src module (handles kebab-case filenames)."""
    spec = importlib.util.spec_from_file_location(
        module_name,
        Path(__file__).parent / f"{module_name}.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ─── NEW PROJECT ───

@app.command()
def new(idea: str = typer.Argument(None, help="Ý tưởng video")):
    """Tạo project mới từ ý tưởng."""
    from src.database import create_project, update_project

    if not idea:
        idea = Prompt.ask("[bold cyan]Nhập ý tưởng video[/]")

    mode = Prompt.ask(
        "[bold]Chọn mode[/]",
        choices=["viral", "product"],
        default="viral"
    )

    console.print(f"\n[bold green]Ý tưởng:[/] {idea}")
    console.print(f"[bold green]Mode:[/] {mode}\n")

    # Ask: auto or manual for script?
    script_mode = Prompt.ask(
        "[bold]Tạo script bằng?[/]",
        choices=["auto", "manual"],
        default="auto"
    )

    project_id = create_project(title=idea, mode=mode)
    console.print(f"[green]✓ Project #{project_id} created[/]\n")

    if script_mode == "auto":
        _generate_script_auto(project_id, idea, mode)
    else:
        _generate_script_manual(project_id, idea, mode)


def _generate_script_auto(project_id: int, idea: str, mode: str):
    """Generate script via Gemini API."""
    from src.database import update_project, add_asset
    gemini = _import("gemini-client")

    with console.status("[bold yellow]Đang tạo script bằng Gemini API...[/]"):
        try:
            result = gemini.generate_script(idea, mode)
        except Exception as e:
            console.print(f"[red]Lỗi API: {e}[/]")
            console.print("[yellow]Chuyển sang manual mode...[/]")
            _generate_script_manual(project_id, idea, mode)
            return

    # Display result
    console.print(Panel(result["script"], title=f"[bold]{result['title']}[/]", border_style="green"))
    console.print(f"[cyan]Hook:[/] {result.get('hook', '')}")
    console.print(f"[cyan]Hashtags:[/] {' '.join(result.get('hashtags', []))}")
    console.print(f"[cyan]Scenes:[/]")
    for i, scene in enumerate(result.get("scenes", []), 1):
        console.print(f"  {i}. {scene}")

    # Save to project
    update_project(project_id, script=json.dumps(result, ensure_ascii=False),
                   title=result.get("title", idea))

    add_asset("text", "script", result["filename"],
              tags=["script", mode], source="gemini-api",
              prompt=idea, project_id=project_id)

    console.print(f"\n[green]✓ Script saved[/] → {result['filename']}")

    # Next step
    if Confirm.ask("\n[bold]Tiếp tục tạo voice?[/]", default=True):
        voice(project_id=project_id)


def _generate_script_manual(project_id: int, idea: str, mode: str):
    """Generate prompts for manual Gemini Web usage."""
    gemini = _import("gemini-client")

    prompts = gemini.generate_prompt_for_web(idea, mode)

    console.print("\n[bold yellow]═══ PROMPTS CHO GEMINI WEB ═══[/]\n")

    console.print(Panel(prompts["script_prompt"],
                       title="[bold]1. Script Prompt[/] (copy → paste vào Gemini)", border_style="cyan"))

    for i, p in enumerate(prompts["image_prompts"], 1):
        console.print(Panel(p, title=f"[bold]2.{i} Image Prompt[/]", border_style="magenta"))

    console.print(Panel(prompts["voice_prompt"],
                       title="[bold]3. Voice Prompt[/]", border_style="yellow"))

    console.print(f"\n[green]✓ Prompts saved[/] → {prompts['filename']}")
    console.print("\n[bold]Sau khi tạo xong trên Gemini Web:[/]")
    console.print("  1. Tải file về")
    console.print("  2. Chạy: [cyan]py -m src.cli import <file_or_folder>[/]")


# ─── VOICE GENERATION ───

@app.command()
def voice(project_id: int = typer.Option(None, help="Project ID"),
          text: str = typer.Option(None, help="Text to convert")):
    """Tạo voiceover bằng Edge TTS (free, tiếng Việt)."""
    from src.database import get_project, add_asset
    tts = _import("tts-engine")

    # Get text from project script or argument
    if not text and project_id:
        project = get_project(project_id)
        if project and project["script"]:
            script_data = json.loads(project["script"])
            text = script_data.get("script", "")

    if not text:
        text = Prompt.ask("[bold cyan]Nhập text cho voiceover[/]")

    # Choose voice
    voices = tts.list_voices()
    console.print("\n[bold]Giọng đọc:[/]")
    for key, name in voices.items():
        console.print(f"  [cyan]{key}[/]: {name}")

    voice_key = Prompt.ask("[bold]Chọn giọng[/]",
                          choices=list(voices.keys()),
                          default="female_south")

    with console.status("[bold yellow]Đang tạo voiceover...[/]"):
        filepath = tts.generate_voice(text, voice_key)

    add_asset("audio", "voiceover", filepath,
              tags=["voiceover", voice_key], source="edge-tts",
              prompt=text[:200], project_id=project_id)

    console.print(f"\n[green]✓ Voice saved[/] → {filepath}")

    if project_id and Confirm.ask("\n[bold]Tiếp tục tạo video?[/]", default=True):
        assemble(project_id=project_id)


# ─── IMPORT ASSETS ───

@app.command(name="import")
def import_assets(path: str = typer.Argument(help="File or folder to import"),
                  tags: str = typer.Option("", help="Comma-separated tags"),
                  source: str = typer.Option("manual", help="Source name"),
                  project_id: int = typer.Option(None, help="Project ID")):
    """Import file/folder vào asset system."""
    importer = _import("asset-importer")

    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    p = Path(path)

    if p.is_dir():
        results = importer.import_folder(str(p), tags=tag_list,
                                         source=source, project_id=project_id)
        for r in results:
            console.print(f"[green]✓[/] {r['type']}: {r['name']} → {r['path']}")
        console.print(f"\n[bold green]Imported {len(results)} files[/]")
    elif p.is_file():
        result = importer.import_file(str(p), tags=tag_list,
                                      source=source, project_id=project_id)
        console.print(f"[green]✓[/] {result['type']}: {result['name']} → {result['path']}")
    else:
        console.print(f"[red]Not found: {path}[/]")


# ─── VIDEO ASSEMBLY ───

@app.command()
def assemble(project_id: int = typer.Option(None, help="Project ID"),
             images: str = typer.Option(None, help="Comma-separated image paths"),
             audio: str = typer.Option(None, help="Audio file path"),
             music: str = typer.Option(None, help="Background music path")):
    """Ghép ảnh + voice thành video TikTok 9:16."""
    from src.database import search_assets, update_project
    assembler = _import("video-assembler")

    # Get assets from project or arguments
    image_list = []
    audio_path = audio

    if project_id:
        if not images:
            found = search_assets(asset_type="image", keyword=None)
            project_images = [a for a in found if a.get("project_id") == project_id]
            if project_images:
                image_list = [a["file_path"] for a in project_images]

        if not audio_path:
            found = search_assets(asset_type="audio", keyword=None)
            project_audio = [a for a in found if a.get("project_id") == project_id]
            if project_audio:
                audio_path = project_audio[0]["file_path"]

    if images:
        image_list = [i.strip() for i in images.split(",")]

    if not image_list:
        console.print("[red]Cần ít nhất 1 ảnh. Dùng --images hoặc import ảnh vào project.[/]")
        raise typer.Exit(1)
    if not audio_path:
        console.print("[red]Cần file audio. Dùng --audio hoặc tạo voice trước.[/]")
        raise typer.Exit(1)

    console.print(f"[cyan]Images:[/] {len(image_list)} files")
    console.print(f"[cyan]Audio:[/] {audio_path}")

    with console.status("[bold yellow]Đang ghép video...[/]"):
        video_path = assembler.create_slideshow(image_list, audio_path)

    console.print(f"\n[green]✓ Video created[/] → {video_path}")

    # Optional background music
    if music:
        with console.status("[bold yellow]Đang thêm nhạc nền...[/]"):
            video_path = assembler.add_background_music(video_path, music)
        console.print(f"[green]✓ Music added[/] → {video_path}")

    if project_id:
        update_project(project_id, status="review")
        console.print(f"\n[bold]Project #{project_id} → status: review[/]")


# ─── LIST / STATUS ───

@app.command()
def projects(status: str = typer.Option(None, help="Filter by status")):
    """Danh sách projects."""
    from src.database import list_projects

    items = list_projects(status=status)
    if not items:
        console.print("[yellow]Chưa có project nào.[/]")
        return

    table = Table(title="Projects")
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("Mode", style="magenta")
    table.add_column("Status", style="green")
    table.add_column("Created", style="dim")

    for p in items:
        table.add_row(str(p["id"]), p["title"], p["mode"],
                      p["status"], p["created_at"][:16])

    console.print(table)


@app.command()
def assets(asset_type: str = typer.Option(None, help="Filter: image/video/audio/text"),
           keyword: str = typer.Option(None, help="Search keyword")):
    """Danh sách assets."""
    from src.database import search_assets

    items = search_assets(asset_type=asset_type, keyword=keyword)
    if not items:
        console.print("[yellow]Chưa có asset nào.[/]")
        return

    table = Table(title="Assets")
    table.add_column("ID", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Name", style="white")
    table.add_column("Source", style="green")
    table.add_column("Tags", style="dim")

    for a in items:
        table.add_row(str(a["id"]), a["type"], a["name"],
                      a["source"], a["tags"][:30])

    console.print(table)


if __name__ == "__main__":
    app()
