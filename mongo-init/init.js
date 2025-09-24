// Initialize the university_recommender database
db = db.getSiblingDB('university_recommender');

// Create collections with validation
db.createCollection('students', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['email', 'password', 'firstName', 'lastName'],
      properties: {
        email: {
          bsonType: 'string',
          pattern: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
        },
        password: {
          bsonType: 'string',
          minLength: 6
        },
        firstName: {
          bsonType: 'string',
          maxLength: 50
        },
        lastName: {
          bsonType: 'string',
          maxLength: 50
        },
        yearGroup: {
          bsonType: 'string',
          enum: ['Year 11', 'Year 12', 'Year 13']
        },
        aLevelSubjects: {
          bsonType: 'array',
          items: {
            bsonType: 'string'
          }
        },
        predictedGrades: {
          bsonType: 'object'
        },
        preferences: {
          bsonType: 'object'
        }
      }
    }
  }
});

db.createCollection('courses', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['name', 'university', 'entryRequirements', 'fees'],
      properties: {
        name: {
          bsonType: 'string',
          maxLength: 200
        },
        university: {
          bsonType: 'object',
          required: ['name'],
          properties: {
            name: {
              bsonType: 'string'
            },
            ranking: {
              bsonType: 'object'
            }
          }
        },
        entryRequirements: {
          bsonType: 'object',
          required: ['subjects', 'grades']
        },
        fees: {
          bsonType: 'object',
          required: ['uk']
        }
      }
    }
  }
});

db.createCollection('universities', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['name'],
      properties: {
        name: {
          bsonType: 'string'
        },
        location: {
          bsonType: 'string'
        },
        ranking: {
          bsonType: 'object'
        }
      }
    }
  }
});

db.createCollection('recommendations', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['studentId', 'criteria', 'recommendations'],
      properties: {
        studentId: {
          bsonType: 'objectId'
        },
        criteria: {
          bsonType: 'object'
        },
        recommendations: {
          bsonType: 'array'
        }
      }
    }
  }
});

// Create indexes for better performance
db.students.createIndex({ email: 1 }, { unique: true });
db.students.createIndex({ yearGroup: 1 });

db.courses.createIndex({ 'university.name': 1 });
db.courses.createIndex({ subjects: 1 });
db.courses.createIndex({ 'entryRequirements.subjects': 1 });
db.courses.createIndex({ 'fees.uk': 1 });

db.universities.createIndex({ name: 1 }, { unique: true });
db.universities.createIndex({ location: 1 });

db.recommendations.createIndex({ studentId: 1 });
db.recommendations.createIndex({ createdAt: -1 });

print('Database initialized successfully!');