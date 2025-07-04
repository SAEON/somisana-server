def compare_products(product, product_json):
    assert (
               product.id,
               product.title,
               product.description,
               product.doi,
               float(product.north_bound),
               float(product.south_bound),
               float(product.east_bound),
               float(product.west_bound),
               product.horizontal_resolution,
               product.vertical_extent,
               product.vertical_resolution,
               product.temporal_extent,
               product.temporal_resolution,
               product.variables,
           ) == (
               product_json['id'],
               product_json['title'],
               product_json['description'],
               product_json['doi'],
               product_json['north_bound'],
               product_json['south_bound'],
               product_json['east_bound'],
               product_json['west_bound'],
               product_json['horizontal_resolution'],
               product_json['vertical_extent'],
               product_json['vertical_resolution'],
               product_json['temporal_extent'],
               product_json['temporal_resolution'],
               product_json['variables']
           )


def compare_datasets(dataset, dataset_json):
    assert (
               int(dataset.id),
               dataset.product_id,
               dataset.title,
               dataset.folder_path
           ) == (
               int(dataset_json['id']),
               dataset_json['product_id'],
               dataset_json['title'],
               dataset_json['folder_path']
           )


def compare_resources(resource, resource_json):
    assert (
               int(resource.id),
               resource.title,
               resource.reference,
               resource.resource_type,
               resource.reference_type
           ) == (
               int(resource_json['id']),
               resource_json['title'],
               resource_json['reference'],
               resource_json['resource_type'],
               resource_json['reference_type']
           )
