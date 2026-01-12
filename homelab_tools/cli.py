"""
CLI entry point for homelab-tools
"""

import json
import sys
from pathlib import Path

import click

from .config import Config
from .logging import setup_logging
from .modules.backup import BackupManager
from .modules.restore import RestoreManager
from .modules.health_check import HealthChecker
from .modules.storage import StorageBoxManager
from .modules.performance import PerformanceMonitor
from .modules.git_hooks import GitHooksManager


# Initialize logger
logger = setup_logging("cli")


@click.group()
@click.option("--config", "-c", help="Path to config file")
@click.pass_context
def cli(ctx, config):
    """Homelab management CLI tool"""
    ctx.ensure_object(dict)
    ctx.obj["config"] = Config(config_path=config)


@cli.group()
def backup():
    """Backup operations"""
    pass


@backup.command("create")
@click.option("--type", "-t", default="full", type=click.Choice(["full", "config", "database"]))
@click.option("--repository", "-r", default="primary", type=click.Choice(["primary", "secondary"]))
@click.pass_context
def backup_create(ctx, type, repository):
    """Create backup"""
    config = ctx.obj["config"]
    manager = BackupManager(config)

    success = manager.create(backup_type=type, repository=repository)
    sys.exit(0 if success else 1)


@backup.command("list")
@click.option("--repository", "-r", default="primary", type=click.Choice(["primary", "secondary"]))
@click.pass_context
def backup_list(ctx, repository):
    """List backups"""
    config = ctx.obj["config"]
    manager = BackupManager(config)

    archives = manager.list(repository=repository)
    for archive in archives:
        click.echo(f"{archive.get('name')} - {archive.get('time', 'Unknown')}")


@backup.command("prune")
@click.option("--repository", "-r", default="primary", type=click.Choice(["primary", "secondary"]))
@click.option("--keep-daily", default=14, type=int)
@click.option("--keep-weekly", default=12, type=int)
@click.option("--keep-monthly", default=24, type=int)
@click.pass_context
def backup_prune(ctx, repository, keep_daily, keep_weekly, keep_monthly):
    """Prune old backups"""
    config = ctx.obj["config"]
    manager = BackupManager(config)

    success = manager.prune(repository, keep_daily, keep_weekly, keep_monthly)
    sys.exit(0 if success else 1)


@backup.command("verify")
@click.option("--repository", "-r", default="primary", type=click.Choice(["primary", "secondary"]))
@click.pass_context
def backup_verify(ctx, repository):
    """Verify repository integrity"""
    config = ctx.obj["config"]
    manager = BackupManager(config)

    success = manager.verify(repository)
    sys.exit(0 if success else 1)


@cli.group()
def restore():
    """Restore operations"""
    pass


@restore.command("list")
@click.option("--repository", "-r", default="primary", type=click.Choice(["primary", "secondary"]))
@click.pass_context
def restore_list(ctx, repository):
    """List available archives"""
    config = ctx.obj["config"]
    manager = RestoreManager(config)

    archives = manager.list(repository=repository)
    for archive in archives:
        click.echo(f"{archive.get('name')} - {archive.get('time', 'Unknown')}")


@restore.command("extract")
@click.argument("archive_name")
@click.option("--target", "-t", help="Target directory")
@click.option("--repository", "-r", default="primary", type=click.Choice(["primary", "secondary"]))
@click.pass_context
def restore_extract(ctx, archive_name, target, repository):
    """Extract archive"""
    config = ctx.obj["config"]
    manager = RestoreManager(config)

    success = manager.extract(archive_name, target, repository)
    sys.exit(0 if success else 1)


@restore.command("verify")
@click.argument("archive_name")
@click.option("--repository", "-r", default="primary", type=click.Choice(["primary", "secondary"]))
@click.pass_context
def restore_verify(ctx, archive_name, repository):
    """Verify archive integrity"""
    config = ctx.obj["config"]
    manager = RestoreManager(config)

    success = manager.verify(archive_name, repository)
    sys.exit(0 if success else 1)


@restore.command("systemd")
@click.argument("archive_name")
@click.option("--repository", "-r", default="primary", type=click.Choice(["primary", "secondary"]))
@click.option("--dry-run", is_flag=True, help="Show what would be restored without actually restoring")
@click.pass_context
def restore_systemd(ctx, archive_name, repository, dry_run):
    """Restore systemd files from backup to /etc/systemd/system/"""
    config = ctx.obj["config"]
    manager = RestoreManager(config)

    success = manager.restore_systemd_files(archive_name, repository, dry_run)
    sys.exit(0 if success else 1)


@cli.command("health-check")
@click.option("--local/--remote", default=True, help="Run locally or via SSH")
@click.option("--host", help="SSH host (for remote mode)")
@click.option("--json", "output_json", is_flag=True, help="Output JSON")
@click.pass_context
def health_check(ctx, local, host, output_json):
    """Run health checks"""
    config = ctx.obj["config"]
    checker = HealthChecker(config, local=local)

    if local:
        results = checker.check_all()
    else:
        results = checker.check_remote(host)

    if output_json:
        click.echo(json.dumps(results, indent=2))
    else:
        # Pretty print
        click.echo(f"Health Check Results ({results.get('timestamp', 'Unknown')})")
        click.echo(f"Errors: {len(results.get('errors', []))}")
        for error in results.get("errors", []):
            click.echo(f"  ❌ {error}")

    sys.exit(0 if len(results.get("errors", [])) == 0 else 1)


@cli.group()
def storage():
    """Storage Box operations"""
    pass


@storage.command("mount")
@click.option("--box", "-b", default="main", type=click.Choice(["main", "immich", "all"]))
@click.option("--method", "-m", default="webdav", type=click.Choice(["webdav", "ssh"]))
@click.pass_context
def storage_mount(ctx, box, method):
    """Mount Storage Box"""
    config = ctx.obj["config"]
    manager = StorageBoxManager(config)

    if box == "all":
        success = True
        for box_name in ["main", "immich"]:
            if not manager.mount(box_name, method):
                success = False
    else:
        success = manager.mount(box, method)

    sys.exit(0 if success else 1)


@storage.command("unmount")
@click.option("--box", "-b", default="main", type=click.Choice(["main", "immich", "all"]))
@click.pass_context
def storage_unmount(ctx, box):
    """Unmount Storage Box"""
    config = ctx.obj["config"]
    manager = StorageBoxManager(config)

    if box == "all":
        success = True
        for box_name in ["main", "immich"]:
            if not manager.unmount(box_name):
                success = False
    else:
        success = manager.unmount(box)

    sys.exit(0 if success else 1)


@storage.command("status")
@click.option("--box", "-b", help="Box name (default: all)")
@click.pass_context
def storage_status(ctx, box):
    """Show Storage Box status"""
    config = ctx.obj["config"]
    manager = StorageBoxManager(config)

    status = manager.status(box)
    click.echo(json.dumps(status, indent=2))


@storage.command("setup")
@click.option("--box", "-b", default="main", type=click.Choice(["main", "immich"]))
@click.option("--method", "-m", default="webdav", type=click.Choice(["webdav", "ssh"]))
@click.pass_context
def storage_setup(ctx, box, method):
    """Setup systemd units for Storage Box"""
    config = ctx.obj["config"]
    manager = StorageBoxManager(config)

    success = manager.setup_systemd(box, method)
    sys.exit(0 if success else 1)


@storage.command("sync-systemd")
@click.pass_context
def storage_sync_systemd(ctx):
    """Sync systemd files from /etc/systemd/system/ to /opt/homelab/systemd/"""
    config = ctx.obj["config"]
    manager = StorageBoxManager(config)

    success = manager.sync_systemd_files()
    sys.exit(0 if success else 1)


@cli.group()
def performance():
    """Performance monitoring"""
    pass


@performance.command("check")
@click.option("--service", "-s", help="Service to check (default: all)")
@click.option("--json", "output_json", is_flag=True, help="Output JSON")
@click.pass_context
def performance_check(ctx, service, output_json):
    """Check performance metrics"""
    config = ctx.obj["config"]
    monitor = PerformanceMonitor(config)

    results = monitor.check(service)

    if output_json:
        click.echo(json.dumps(results, indent=2))
    else:
        click.echo(f"Performance Check ({results.get('timestamp', 'Unknown')})")
        click.echo(json.dumps(results, indent=2))


@performance.command("report")
@click.option("--format", "-f", default="json", type=click.Choice(["json", "html", "slack"]))
@click.option("--output", "-o", help="Output file")
@click.option("--service", "-s", help="Service to report on")
@click.pass_context
def performance_report(ctx, format, output, service):
    """Generate performance report"""
    config = ctx.obj["config"]
    monitor = PerformanceMonitor(config)

    monitor.generate_report(format, output, service)


@performance.command("slack")
@click.option("--service", "-s", help="Service to report on")
@click.pass_context
def performance_slack(ctx, service):
    """Send performance report to Slack"""
    config = ctx.obj["config"]
    monitor = PerformanceMonitor(config)

    success = monitor.send_slack_report(service)
    sys.exit(0 if success else 1)


@cli.group()
def git_hooks():
    """Git hooks management"""
    pass


@git_hooks.command("install")
@click.pass_context
def git_hooks_install(ctx):
    """Install Git hooks"""
    manager = GitHooksManager()
    success = manager.install()
    sys.exit(0 if success else 1)


@git_hooks.command("uninstall")
@click.pass_context
def git_hooks_uninstall(ctx):
    """Remove Git hooks"""
    manager = GitHooksManager()
    success = manager.uninstall()
    sys.exit(0 if success else 1)


@git_hooks.command("test")
@click.pass_context
def git_hooks_test(ctx):
    """Test Git hooks locally"""
    manager = GitHooksManager()
    success = manager.test()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    cli()
