using System.ComponentModel.DataAnnotations;

namespace Poe2scout.ValidationAttributes;

public class MultipleOfFourAttribute : ValidationAttribute
{
  protected override ValidationResult? IsValid(object? value, ValidationContext validationContext)
  {
    if (value is int year && year % 4 == 0)
    {
      return ValidationResult.Success;
    }
    
    return new ValidationResult("Must be a multiple of four.");
  }
}