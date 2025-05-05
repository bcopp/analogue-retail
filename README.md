# Quick start
- ensure Docker is installed
- make up
- http://localhost:3000/

# Test
The test hits these api endpoints
- Post    `/add`
- Delete  `/remove/{product_id}`
- Get     `/search?name=...` (Implements fuzzy search)
- Get     `/analytics/view/{product_id}`

# Output
```
INFO:__main__:Successfully uploaded sample.jpg to S3 with key brendanheadshot
INFO:__main__:Added product: beer with ID 1046
INFO:__main__:Added product: beers with ID 6047
INFO:__main__:Added product: be with ID 3992
INFO:__main__:Added product: beer4 with ID 7646
INFO:__main__:Added product: apple with ID 1385
INFO:__main__:Added product: beer5 with ID 4677
INFO:__main__:Added product: beer6 with ID 6221
INFO:__main__:Added product: beer7 with ID 6956
INFO:__main__:Added product: beer8 with ID 9411
INFO:__main__:Added product: beer9 with ID 1538
INFO:__main__:Added product: beer10 with ID 3842
INFO:__main__:Removed product with ID 7646
INFO:__main__:Removed product with ID 1385
INFO:__main__:Search results for 'beer':
INFO:__main__:{
  "products": [
    {
      "product_id": 9411,
      "name": "beer8",
      "description": "Description for beer8",
      "image_key": "brendanheadshot",
      "price": 6.73,
      "view_count": null
    },
    {
      "product_id": 6956,
      "name": "beer7",
      "description": "Description for beer7",
      "image_key": "brendanheadshot",
      "price": 3.99,
      "view_count": null
    },
    {
      "product_id": 6221,
      "name": "beer6",
      "description": "Description for beer6",
      "image_key": "brendanheadshot",
      "price": 3.17,
      "view_count": null
    },
    {
      "product_id": 4677,
      "name": "beer5",
      "description": "Description for beer5",
      "image_key": "brendanheadshot",
      "price": 4.26,
      "view_count": null
    },
    {
      "product_id": 3842,
      "name": "beer10",
      "description": "Description for beer10",
      "image_key": "brendanheadshot",
      "price": 3.61,
      "view_count": null
    },
    {
      "product_id": 1538,
      "name": "beer9",
      "description": "Description for beer9",
      "image_key": "brendanheadshot",
      "price": 5.61,
      "view_count": null
    },
    {
      "product_id": 1046,
      "name": "beer",
      "description": "Description for beer",
      "image_key": "brendanheadshot",
      "price": 4.44,
      "view_count": null
    }
  ]
}
INFO:__main__:Viewed product 1046
```
