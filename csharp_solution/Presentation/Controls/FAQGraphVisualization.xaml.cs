using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Shapes;
using UniversalFAQLoader.Business.Models;

namespace UniversalFAQLoader.Presentation.Controls
{
    /// <summary>
    /// Логика взаимодействия для FAQGraphVisualization.xaml
    /// </summary>
    public partial class FAQGraphVisualization : UserControl
    {
        private List<FAQNode> _nodes = new List<FAQNode>();
        private List<FAQConnection> _connections = new List<FAQConnection>();
        private Dictionary<Guid, Point> _nodePositions = new Dictionary<Guid, Point>();
        private Dictionary<Guid, Ellipse> _nodeShapes = new Dictionary<Guid, Ellipse>();
        private Dictionary<Guid, TextBlock> _nodeLabels = new Dictionary<Guid, TextBlock>();

        public FAQGraphVisualization()
        {
            InitializeComponent();
        }

        public void UpdateGraphData(IEnumerable<FAQNode>? nodes, IEnumerable<FAQConnection>? connections)
        {
            _nodes = nodes?.ToList() ?? new List<FAQNode>();
            _connections = connections?.ToList() ?? new List<FAQConnection>();
            RenderGraph();
        }

        private void RefreshButton_Click(object sender, RoutedEventArgs e)
        {
            RenderGraph();
        }

        private void LegendButton_Click(object sender, RoutedEventArgs e)
        {
            LegendPanel.Visibility = Visibility.Visible;
        }

        private void CloseLegendButton_Click(object sender, RoutedEventArgs e)
        {
            LegendPanel.Visibility = Visibility.Collapsed;
        }

        public void RenderGraph()
        {
            // Clear previous graph
            GraphCanvas.Children.Clear();
            _nodePositions.Clear();
            _nodeShapes.Clear();
            _nodeLabels.Clear();

            if (_nodes == null || !_nodes.Any())
                return;

            // Calculate node positions using a simple force-directed layout
            CalculateNodePositions();

            // Draw connections first (so they appear behind nodes)
            DrawConnections();

            // Draw nodes
            DrawNodes();
        }

        private void CalculateNodePositions()
        {
            var random = new Random(42); // Fixed seed for reproducible layouts
            var canvasWidth = Math.Max(GraphCanvas.ActualWidth, 800);
            var canvasHeight = Math.Max(GraphCanvas.ActualHeight, 600);

            // Simple random layout for now - can be improved with force-directed algorithm
            foreach (var node in _nodes)
            {
                var x = random.Next(50, (int)canvasWidth - 100);
                var y = random.Next(50, (int)canvasHeight - 100);
                _nodePositions[node.Id] = new Point(x, y);
            }
        }

        private void DrawConnections()
        {
            if (_connections == null) return;

            foreach (var connection in _connections)
            {
                // Check if both nodes exist
                if (!_nodePositions.ContainsKey(connection.SourceNodeId) || 
                    !_nodePositions.ContainsKey(connection.TargetNodeId))
                    continue;

                var sourcePos = _nodePositions[connection.SourceNodeId];
                var targetPos = _nodePositions[connection.TargetNodeId];

                // Create line for connection
                var line = new Line
                {
                    X1 = sourcePos.X,
                    Y1 = sourcePos.Y,
                    X2 = targetPos.X,
                    Y2 = targetPos.Y,
                    StrokeThickness = 2,
                    Stroke = GetConnectionColor(connection.Type)
                };

                // Set line style based on connection type
                switch (connection.Type)
                {
                    case ConnectionType.Prerequisite:
                        line.StrokeDashArray = new DoubleCollection(new[] { 5.0, 2.0 });
                        break;
                    case ConnectionType.Contradiction:
                        line.StrokeDashArray = new DoubleCollection(new[] { 2.0, 2.0 });
                        break;
                }

                GraphCanvas.Children.Add(line);
            }
        }

        private void DrawNodes()
        {
            const double nodeRadius = 30;

            foreach (var node in _nodes)
            {
                if (!_nodePositions.ContainsKey(node.Id)) continue;

                var position = _nodePositions[node.Id];

                // Create node circle
                var ellipse = new Ellipse
                {
                    Width = nodeRadius * 2,
                    Height = nodeRadius * 2,
                    Fill = new SolidColorBrush(GetNodeColor(node)),
                    Stroke = Brushes.Black,
                    StrokeThickness = 2
                };

                Canvas.SetLeft(ellipse, position.X - nodeRadius);
                Canvas.SetTop(ellipse, position.Y - nodeRadius);
                GraphCanvas.Children.Add(ellipse);
                _nodeShapes[node.Id] = ellipse;

                // Create node label (abbreviated query)
                var query = node.Query ?? "Неизвестный узел";
                var labelText = query.Length > 15 ? query.Substring(0, 12) + "..." : query;
                var textBlock = new TextBlock
                {
                    Text = labelText,
                    Foreground = Brushes.White,
                    FontSize = 10,
                    TextAlignment = TextAlignment.Center,
                    FontWeight = FontWeights.Bold
                };

                Canvas.SetLeft(textBlock, position.X - nodeRadius);
                Canvas.SetTop(textBlock, position.Y - 5);
                Canvas.SetZIndex(textBlock, 10); // Ensure text is above shapes
                GraphCanvas.Children.Add(textBlock);
                _nodeLabels[node.Id] = textBlock;
            }
        }

        private Color GetNodeColor(FAQNode node)
        {
            // Color based on node metadata or type
            var hue = (node.Metadata.AccessCount % 360);
            return Color.FromRgb(
                (byte)(Math.Sin(hue * Math.PI / 180) * 127 + 128),
                (byte)(Math.Sin((hue + 120) * Math.PI / 180) * 127 + 128),
                (byte)(Math.Sin((hue + 240) * Math.PI / 180) * 127 + 128)
            );
        }

        private Brush GetConnectionColor(ConnectionType type)
        {
            return type switch
            {
                ConnectionType.Semantic => Brushes.Blue,
                ConnectionType.Prerequisite => Brushes.Red,
                ConnectionType.FollowUp => Brushes.Green,
                ConnectionType.Related => Brushes.Purple,
                ConnectionType.Contradiction => Brushes.Orange,
                ConnectionType.GroupMember => Brushes.Gray,
                ConnectionType.Duplicate => Brushes.Brown,
                ConnectionType.FileReference => Brushes.Cyan,
                ConnectionType.Custom => Brushes.Magenta,
                _ => Brushes.Black
            };
        }
    }
}