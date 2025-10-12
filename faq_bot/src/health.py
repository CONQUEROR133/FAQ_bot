import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
import psutil
import os
from datetime import datetime

router = Router()

# Global variable to track bot start time
start_time = datetime.now()

def get_system_stats():
    """Get system statistics for health check"""
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used = memory.used / (1024**3)  # GB
        memory_total = memory.total / (1024**3)  # GB
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        disk_used = disk.used / (1024**3)  # GB
        disk_total = disk.total / (1024**3)  # GB
        
        # Uptime
        uptime = datetime.now() - start_time
        
        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory_percent,
            'memory_used': round(memory_used, 2),
            'memory_total': round(memory_total, 2),
            'disk_percent': disk_percent,
            'disk_used': round(disk_used, 2),
            'disk_total': round(disk_total, 2),
            'uptime': str(uptime).split('.')[0]  # Remove microseconds
        }
    except Exception as e:
        logging.error(f"Error getting system stats: {e}")
        return None

@router.message(Command("health"))
async def health_check(message: Message):
    """Health check endpoint for monitoring bot status"""
    try:
        # Get system statistics
        stats = get_system_stats()
        
        if stats is None:
            await message.answer("❌ Error retrieving system statistics")
            return
        
        # Format response
        response = (
            "✅ <b>Bot Health Status</b>\n\n"
            f"⏱️ <b>Uptime:</b> {stats['uptime']}\n\n"
            f"🖥️ <b>CPU Usage:</b> {stats['cpu_percent']:.1f}%\n"
            f"🧠 <b>Memory:</b> {stats['memory_used']:.2f}GB / {stats['memory_total']:.2f}GB ({stats['memory_percent']:.1f}%)\n"
            f"💾 <b>Disk:</b> {stats['disk_used']:.2f}GB / {stats['disk_total']:.2f}GB ({stats['disk_percent']:.1f}%)\n\n"
        )
        
        # Add warning if any resource is over 80% usage
        warnings = []
        if stats['cpu_percent'] > 80:
            warnings.append("⚠️ High CPU usage")
        if stats['memory_percent'] > 80:
            warnings.append("⚠️ High memory usage")
        if stats['disk_percent'] > 80:
            warnings.append("⚠️ Low disk space")
            
        if warnings:
            response += "<b>Warnings:</b>\n" + "\n".join(warnings)
        else:
            response += "✅ All systems normal"
            
        await message.answer(response, parse_mode="HTML")
        
    except Exception as e:
        logging.error(f"Error in health check: {e}")
        await message.answer("❌ Error performing health check")

# Additional health check functions that can be used by external monitoring
def is_bot_healthy():
    """Simple health check function for external monitoring"""
    try:
        # Check if the process is running
        current_process = psutil.Process(os.getpid())
        if current_process.is_running():
            return True
        return False
    except Exception as e:
        logging.error(f"Error checking bot health: {e}")
        return False

def get_health_status():
    """Get detailed health status for external monitoring"""
    try:
        stats = get_system_stats()
        if stats is None:
            return {"status": "error", "message": "Failed to get system stats"}
            
        # Determine overall health based on resource usage
        healthy = True
        issues = []
        
        if stats['cpu_percent'] > 90:
            healthy = False
            issues.append("CPU usage over 90%")
        if stats['memory_percent'] > 90:
            healthy = False
            issues.append("Memory usage over 90%")
        if stats['disk_percent'] > 95:
            healthy = False
            issues.append("Disk usage over 95%")
            
        return {
            "status": "healthy" if healthy else "degraded",
            "issues": issues,
            "stats": stats
        }
    except Exception as e:
        logging.error(f"Error getting health status: {e}")
        return {"status": "error", "message": str(e)}