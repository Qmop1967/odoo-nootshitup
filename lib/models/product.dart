class Product {
  final int id;
  final String name;
  final double listPrice;
  final String defaultCode;
  final String category;

  Product({
    required this.id,
    required this.name,
    required this.listPrice,
    required this.defaultCode,
    required this.category,
  });

  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      id: json['id'] ?? 0,
      name: json['name'] ?? '',
      listPrice: (json['list_price'] ?? 0.0).toDouble(),
      defaultCode: json['default_code'] ?? '',
      category: json['categ_id'] is List 
          ? json['categ_id'][1] ?? ''
          : '',
    );
  }

  String get displayName {
    if (defaultCode.isNotEmpty) {
      return '[$defaultCode] $name';
    }
    return name;
  }
} 