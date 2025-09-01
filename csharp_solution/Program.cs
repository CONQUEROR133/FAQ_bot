using System;
using System.Windows;
using UniversalFAQLoader.Presentation.Views;

namespace UniversalFAQLoader
{
    public class Program
    {
        [STAThread]
        public static void Main(string[] args)
        {
            var app = new Application();
            var mainWindow = new MainWindow();
            app.Run(mainWindow);
        }
    }
}