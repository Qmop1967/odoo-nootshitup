class Product {
  final int id;
  final String name;
  final double listPrice;
  final String defaultCode;
  final String category;
  final String? image1920;
  final String? imageMedium;
  final String? imageSmall;

  Product({
    required this.id,
    required this.name,
    required this.listPrice,
    required this.defaultCode,
    required this.category,
    this.image1920,
    this.imageMedium,
    this.imageSmall,
  });

  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      id: json['id'] ?? 0,
      name: json['name'] ?? '',
      listPrice: (json['list_price'] ?? 0.0).toDouble(),
      defaultCode: json['default_code'] ?? '',
      category: json['categ_id'] is List 
          ? json['categ_id'][1] ?? ''
          : json['categ_id']?.toString() ?? '',
      image1920: json['image_1920'],
      imageMedium: json['image_medium'],
      imageSmall: json['image_small'],
    );
  }

  String get displayName {
    if (defaultCode.isNotEmpty) {
      return '[$defaultCode] $name';
    }
    return name;
  }

  // Helper method to get the best available image
  String? get bestImage {
    return imageSmall ?? imageMedium ?? image1920;
  }

  // Helper method to check if product has any image
  bool get hasImage {
    return image1920 != null || imageMedium != null || imageSmall != null;
  }
} 