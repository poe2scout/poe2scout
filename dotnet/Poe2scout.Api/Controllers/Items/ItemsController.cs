using Microsoft.AspNetCore.Mvc;
using Poe2scout.Database;

namespace Poe2scout.Controllers;

[Route("api/[controller]")]
[ApiController]
public partial class ItemsController(IItemRepository itemRepository) : ControllerBase
{
    
}