# RHINO-CAR Performance Optimization System
import psutil
import time
import threading
import json
from collections import deque
from datetime import datetime
import numpy as np

class RhinoPerformanceOptimizer:
    """Advanced performance monitoring and optimization for RHINO-CAR"""
    
    def __init__(self, optimization_level="balanced"):
        self.optimization_level = optimization_level  # conservative, balanced, aggressive
        self.performance_history = deque(maxlen=1000)
        self.optimization_active = False
        
        # Performance thresholds
        self.thresholds = {
            'cpu_warning': 70,     # CPU usage %
            'memory_warning': 75,  # Memory usage %
            'frame_rate_min': 20,  # FPS minimum
            'inference_time_max': 150,  # milliseconds
            'response_time_max': 500    # Voice response time
        }
        
        # Dynamic settings
        self.dynamic_settings = {
            'yolo_confidence': 0.5,
            'video_resolution': (640, 480),
            'processing_interval': 1,  # frames to skip
            'voice_sensitivity': 0.7,
            'model_precision': 'fp32'  # fp16, fp32, int8
        }
        
        # Performance monitoring thread
        self.monitor_thread = None
        self.monitoring = False
        
    def start_performance_monitoring(self):
        """Start background performance monitoring"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._performance_monitor_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            print("🔍 Performance monitoring started")
    
    def stop_performance_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        print("⏹️ Performance monitoring stopped")
    
    def _performance_monitor_loop(self):
        """Main performance monitoring loop"""
        while self.monitoring:
            try:
                # Collect performance metrics
                metrics = self.collect_performance_metrics()
                self.performance_history.append(metrics)
                
                # Check for optimization needs
                if self.needs_optimization(metrics):
                    self.apply_performance_optimizations(metrics)
                
                time.sleep(2)  # Check every 2 seconds
            except Exception as e:
                print(f"Performance monitoring error: {e}")
                time.sleep(5)
    
    def collect_performance_metrics(self):
        """Collect comprehensive system performance metrics"""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # GPU metrics (if available)
            gpu_usage = self.get_gpu_usage()
            
            # Application-specific metrics
            app_metrics = self.get_application_metrics()
            
            metrics = {
                'timestamp': datetime.now(),
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'memory_available': memory.available // (1024**3),  # GB
                'disk_usage': disk.percent,
                'gpu_usage': gpu_usage,
                'frame_rate': app_metrics.get('frame_rate', 0),
                'inference_time': app_metrics.get('inference_time', 0),
                'voice_response_time': app_metrics.get('voice_response_time', 0),
                'active_threads': threading.active_count()
            }
            
            return metrics
            
        except Exception as e:
            print(f"Error collecting metrics: {e}")
            return {'error': str(e), 'timestamp': datetime.now()}
    
    def get_gpu_usage(self):
        """Get GPU usage if available"""
        try:
            import nvidia_ml_py3 as nvml
            nvml.nvmlInit()
            handle = nvml.nvmlDeviceGetHandleByIndex(0)
            gpu_util = nvml.nvmlDeviceGetUtilizationRates(handle)
            return gpu_util.gpu
        except:
            return 0  # No GPU or NVIDIA-ML not available
    
    def get_application_metrics(self):
        """Get RHINO-CAR specific application metrics"""
        # This would be integrated with main application
        # For now, return simulated values
        import random
        return {
            'frame_rate': random.randint(15, 30),
            'inference_time': random.randint(80, 200),
            'voice_response_time': random.randint(200, 800)
        }
    
    def needs_optimization(self, metrics):
        """Determine if performance optimization is needed"""
        if 'error' in metrics:
            return False
            
        # CPU overload
        if metrics['cpu_usage'] > self.thresholds['cpu_warning']:
            return True
            
        # Memory pressure
        if metrics['memory_usage'] > self.thresholds['memory_warning']:
            return True
            
        # Low frame rate
        if metrics['frame_rate'] < self.thresholds['frame_rate_min']:
            return True
            
        # Slow inference
        if metrics['inference_time'] > self.thresholds['inference_time_max']:
            return True
            
        return False
    
    def apply_performance_optimizations(self, metrics):
        """Apply dynamic performance optimizations"""
        if self.optimization_active:
            return  # Don't stack optimizations
            
        self.optimization_active = True
        optimizations_applied = []
        
        try:
            # High CPU usage optimizations
            if metrics['cpu_usage'] > self.thresholds['cpu_warning']:
                # Reduce YOLO confidence threshold for faster processing
                if self.dynamic_settings['yolo_confidence'] > 0.3:
                    self.dynamic_settings['yolo_confidence'] = max(0.3, 
                        self.dynamic_settings['yolo_confidence'] - 0.1)
                    optimizations_applied.append("Reduced YOLO confidence")
                
                # Skip more frames
                if self.dynamic_settings['processing_interval'] < 3:
                    self.dynamic_settings['processing_interval'] += 1
                    optimizations_applied.append("Increased frame skipping")
            
            # High memory usage optimizations
            if metrics['memory_usage'] > self.thresholds['memory_warning']:
                # Reduce video resolution
                current_res = self.dynamic_settings['video_resolution']
                if current_res[0] > 320:
                    new_res = (max(320, current_res[0] - 160), 
                              max(240, current_res[1] - 120))
                    self.dynamic_settings['video_resolution'] = new_res
                    optimizations_applied.append(f"Reduced resolution to {new_res}")
                
                # Switch to lower precision if possible
                if self.dynamic_settings['model_precision'] == 'fp32':
                    self.dynamic_settings['model_precision'] = 'fp16'
                    optimizations_applied.append("Switched to FP16 precision")
            
            # Low frame rate optimizations
            if metrics['frame_rate'] < self.thresholds['frame_rate_min']:
                # More aggressive frame skipping
                if self.dynamic_settings['processing_interval'] < 4:
                    self.dynamic_settings['processing_interval'] = 3
                    optimizations_applied.append("Aggressive frame skipping enabled")
            
            # Slow inference optimizations
            if metrics['inference_time'] > self.thresholds['inference_time_max']:
                # Reduce confidence threshold further
                if self.dynamic_settings['yolo_confidence'] > 0.2:
                    self.dynamic_settings['yolo_confidence'] = 0.35
                    optimizations_applied.append("Lowered detection threshold")
            
            if optimizations_applied:
                print(f"🚀 Performance optimizations applied: {', '.join(optimizations_applied)}")
                
                # Voice notification if enabled
                try:
                    from llm_handler import speak_text
                    speak_text("Performance optimization applied for better system response")
                except:
                    pass
            
        except Exception as e:
            print(f"Error applying optimizations: {e}")
        finally:
            self.optimization_active = False
    
    def get_optimization_suggestions(self, metrics=None):
        """Get manual optimization suggestions"""
        if not metrics and self.performance_history:
            metrics = self.performance_history[-1]
        elif not metrics:
            return "No performance data available yet"
        
        suggestions = []
        
        # CPU suggestions
        if metrics.get('cpu_usage', 0) > 60:
            suggestions.append("• Close unnecessary applications to reduce CPU load")
            suggestions.append("• Consider reducing video quality for better performance")
        
        # Memory suggestions  
        if metrics.get('memory_usage', 0) > 70:
            suggestions.append("• Close browser tabs and unused programs")
            suggestions.append("• Restart RHINO-CAR if memory usage is consistently high")
        
        # Frame rate suggestions
        if metrics.get('frame_rate', 30) < 25:
            suggestions.append("• Reduce camera resolution in settings")
            suggestions.append("• Enable performance mode for faster processing")
        
        # General suggestions
        suggestions.append("• Ensure good ventilation to prevent thermal throttling")
        suggestions.append("• Update GPU drivers for optimal performance")
        
        return "\n".join(suggestions) if suggestions else "System performance looks good!"
    
    def reset_optimizations(self):
        """Reset all dynamic optimizations to default values"""
        self.dynamic_settings = {
            'yolo_confidence': 0.5,
            'video_resolution': (640, 480),
            'processing_interval': 1,
            'voice_sensitivity': 0.7,
            'model_precision': 'fp32'
        }
        print("🔄 Performance settings reset to defaults")
    
    def get_performance_report(self):
        """Generate comprehensive performance report"""
        if not self.performance_history:
            return "No performance data collected yet"
        
        # Calculate averages from recent history
        recent_metrics = list(self.performance_history)[-100:]  # Last 100 measurements
        
        avg_cpu = np.mean([m.get('cpu_usage', 0) for m in recent_metrics])
        avg_memory = np.mean([m.get('memory_usage', 0) for m in recent_metrics])
        avg_fps = np.mean([m.get('frame_rate', 0) for m in recent_metrics])
        avg_inference = np.mean([m.get('inference_time', 0) for m in recent_metrics])
        
        # Performance grade
        performance_score = 100
        if avg_cpu > 70: performance_score -= 20
        if avg_memory > 75: performance_score -= 20
        if avg_fps < 20: performance_score -= 30
        if avg_inference > 150: performance_score -= 15
        
        grade = "Excellent" if performance_score >= 85 else \
                "Good" if performance_score >= 70 else \
                "Fair" if performance_score >= 55 else "Needs Improvement"
        
        report = f"""
🎯 RHINO-CAR Performance Report
{'='*40}
Overall Grade: {grade} ({performance_score}/100)

📊 System Metrics (Recent Average):
• CPU Usage: {avg_cpu:.1f}%
• Memory Usage: {avg_memory:.1f}%
• Frame Rate: {avg_fps:.1f} FPS
• Inference Time: {avg_inference:.1f}ms

🔧 Current Optimizations:
• YOLO Confidence: {self.dynamic_settings['yolo_confidence']}
• Resolution: {self.dynamic_settings['video_resolution']}
• Frame Skip: {self.dynamic_settings['processing_interval']}
• Model Precision: {self.dynamic_settings['model_precision']}

📈 Recommendations:
{self.get_optimization_suggestions()}
        """
        
        return report.strip()
    
    def voice_performance_command(self, command):
        """Handle voice commands related to performance"""
        command_lower = command.lower()
        
        if 'performance report' in command_lower or 'system status' in command_lower:
            return "Generating performance report. Check console for detailed metrics."
        
        elif 'optimize' in command_lower or 'speed up' in command_lower:
            self.reset_optimizations()
            return "Optimization settings reset. Performance monitoring will auto-adjust as needed."
        
        elif 'performance suggestions' in command_lower:
            suggestions = self.get_optimization_suggestions()
            return f"Performance suggestions: {suggestions[:200]}..."  # Truncate for voice
        
        elif 'reset performance' in command_lower:
            self.reset_optimizations()
            return "Performance settings have been reset to default values."
        
        else:
            return "Performance commands: performance report, optimize system, performance suggestions, reset performance."

# Global performance optimizer instance
rhino_optimizer = RhinoPerformanceOptimizer()

def start_performance_optimization():
    """Start performance monitoring for RHINO-CAR"""
    rhino_optimizer.start_performance_monitoring()
    return rhino_optimizer

def get_current_performance_settings():
    """Get current dynamic performance settings"""
    return rhino_optimizer.dynamic_settings.copy()
