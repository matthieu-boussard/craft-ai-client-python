# **craft ai** API python client #

[![PyPI](https://img.shields.io/pypi/v/craft-ai.svg?style=flat-square)](https://pypi.python.org/pypi?:action=display&name=craft-ai) [![Build Status](https://img.shields.io/travis/craft-ai/craft-ai-client-python/master.svg?style=flat-square)](https://travis-ci.org/craft-ai/craft-ai-client-python) [![License](https://img.shields.io/badge/license-BSD--3--Clause-42358A.svg?style=flat-square)](LICENSE) [![python](https://img.shields.io/pypi/pyversions/craft-ai.svg?style=flat-square)](https://pypi.python.org/pypi?:action=display&name=craft-ai)

[**craft ai** _AI-as-a-service_](http://craft.ai) enables developers to create Apps and Things that adapt to each user. To go beyond useless dashboards and spammy notifications, **craft ai** learns how users behave to automate recurring tasks, make personalized recommendations, or detect anomalies.

## Get Started! ##

### 0 - Signup ###

If you're reading this you are probably already registered with **craft ai**, if not, head to [`https://beta.craft.ai/signup`](https://beta.craft.ai/signup).

> :construction: **craft ai** is currently in private beta, as such we validate accounts, this step should be quick.

### 1 - Retrieve your credentials ###

Once your account is setup, you need to retrieve your **owner** and **token**. Both are available in the 'Settings' tab in the **craft ai** control center at [`https://beta.craft.ai/settings`](https://beta.craft.ai/settings).

### 2 - Setup ###

#### Install ####

#### [PIP](https://pypi.python.org/pypi/pip/) / [PyPI](https://pypi.python.org/pypi) ####

Let's first install the package from pip.

```sh
pip install --upgrade craft-ai
```
Then import it in your code

```python
from craftai import client as craftai
```

#### Initialize ####

```python
config = {
    "owner": '{owner}',
    "token": '{token}'
}
client = craftai.CraftAIClient(config)
```

### 3 - Create an agent ###

**craft ai** is based on the concept of **agents**. In most use cases, one agent is created per user or per device.

An agent is an independent module that stores the history of the **context** of its user or device's context, and learns which **decision** to take based on the evolution of this context in the form of a **decision tree**.

In this example, we will create an agent that learns the **decision model** of a light bulb based on the time of the day and the number of people in the room. In practice, it means the agent's context have 4 properties:

- `peopleCount` which is a `continuous` property,
- `timeOfDay` which is a `time_of_day` property,
- `tz`, a property of type `timezone` needed to generate proper values for `timeOfDay` (cf. the [context properties type section](#context-properties-types) for further information),
- and finally `lightbulbState` which is an `enum` property that is also the output of this model.

```python
agent_id = "my_first_agent"
model = {
    "context": {
        "peopleCount": {
            "type": 'continuous'
        },
        "timeOfDay": {
            "type": 'time_of_day'
        },
        "tz": {
            "type": 'timezone'
        },
        "lightbulbState": {
            "type": 'enum'
        }
    },
    "output": ['lightbulbState']
}

agent = client.create_agent(model, agent_id)
print("Agent", agent["id"], "was successfully created")
```

Pretty straightforward to test! Open [`https://beta.craft.ai/inspector`](https://beta.craft.ai/inspector), your agent is now listed.

Now, if you run that a second time, you'll get an error: the agent `'my_first_agent'` is already existing. Let's see how we can delete it before recreating it.

```python
agent_id = "my_first_agent"
client.delete_agent(agent_id)
print("Agent", agent_id, "no longer exists")

model = ...
agent = client.create_agent(model, agent_id)
print("Agent", agent["id"], "was successfully created")
```

_For further information, check the ['create agent' reference documentation](#create)._

### 4 - Add context operations ###

We have now created our first agent but it is not able to do much, yet. To learn a decision model it needs to be provided with data, in **craft ai** these are called context operations.

In the following we add 8 operations:

1. The initial one sets the initial state of the agent, on July the 25th of 2016 at 5:30, in Paris, nobody is there and the light is off;
2. At 7:02, someone enters the room the light is turned on;
3. At 7:15, someone else enters the room;
4. At 7:31, the light is turned off;
5. At 8:12, everyone leaves the room;
6. At 19:23, 2 persons enter the room;
7. At 22:35, the light is turned on;
8. At 23:06, everyone leaves the room and the light is turned off.

```python
agent_id = "my_first_agent"
client.delete_agent(agent_id)
print("Agent", agent_id, "no longer exists")

model = ...
agent = client.create_agent(model, agent_id)
print("Agent", agent["id"], "was successfully created")

context_list = [
    {
        "timestamp": 1469410200,
        "diff": {
            "tz": '+02:00',
            "peopleCount": 0,
            "lightbulbState": 'OFF'
        }
    },
    {
        "timestamp": 1469415720,
        "diff": {
            "peopleCount": 1,
            "lightbulbState": 'ON'
        }
    },
    {
        "timestamp": 1469416500,
        "diff": {
            "peopleCount": 2
        }
    },
    {
        "timestamp": 1469417460,
        "diff": {
            "lightbulbState": 'OFF'
        }
    },
    {
        "timestamp": 1469419920,
        "diff": {
            "peopleCount": 0
        }
    },
    {
        "timestamp": 1469460180,
        "diff": {
            "peopleCount": 2
        }
    },
    {
        "timestamp": 1469471700,
        "diff": {
            "lightbulbState": 'ON'
        }
    },
    {
        "timestamp": 1469473560,
        "diff": {
            "peopleCount": 0
        }
    }
]
client.add_operations(agent_id, context_list)
print("Successfully added initial operations to agent", agent_id, "!")
```

In real-world applications, you'll probably do the same kind of things when the agent is created and then, regularly throughout the lifetime of the agent with newer data.

_For further information, check the ['add context operations' reference documentation](#add-operations)._

### 5 - Compute the decision tree ###

The agent has acquired a context history, we can now compute a decision tree from it!

The decision tree is computed at a given timestamp, which means it will consider the context history from the creation of this agent up to this moment. Let's first try to compute the decision tree at midnight on July the 26th of 2016.

```python
    agent_id = "my_first_agent"

client.delete_agent(agent_id)
print("Agent", agent_id, "no longer exists")

model = ...
agent = client.create_agent(model, agent_id)
print("Agent", agent["id"], "was successfully created")

context_list = ...
client.add_operations(agent_id, context_list)
print("Successfully added initial operations to agent", agent_id, "!")

resp = client.get_decision_tree(agent_id, 1469476800)
print("The full decision tree at timestamp", dt_timestamp, "is the following:")
print(decision_tree)
```

Try to retrieve the tree at different timestamps to see how it gradually learns from the new operations. To visualize the trees, use the [inspector](https://beta.craft.ai/inspector)!

_For further information, check the ['compute decision tree' reference documentation](#compute)._

### 6 - Take a decision ###

Once the decision tree is computed it can be used to take a decision. In our case it is basically answering this type of question: "What is the anticipated **state of the lightbulb** at 7:15 if there are 2 persons in the room ?".

```python
agent_id = "my_first_agent"

client.delete_agent(agent_id)
print("Agent", agent_id, "no longer exists")

model = ...
agent = client.create_agent(model, agent_id)
print("Agent", agent["id"], "was successfully created")

context_list = ...
client.add_operations(agent_id, context_list)
print("Successfully added initial operations to agent", agent_id, "!")

decision_tree = client.get_decision_tree(agent_id, 1469476800)
print("The decision tree at timestamp", dt_timestamp, "is the following:")
print(decision_tree)

context = {
    "tz": '+02:00',
    "timeOfDay": 7.25,
    "peopleCount": 2
}
resp = client.decide(decision_tree, context)
print("The anticipated lightbulb state is:", resp["decision"]["lightbulbState"])
```

_For further information, check the ['take decision' reference documentation](#take-decision)._

## API ##

### Owner ###

**craft ai** agents belong to **owners**. In the current version, each identified users defines a owner, in the future we will introduce shared organization-level owners.

### Model ###

Each agent is based upon a model, the model defines:

- the context schema, i.e. the list of property keys and their type (as defined in the following section),
- the output properties, i.e. the list of property keys on which the agent takes decisions,

> :warning: In the current version, only one output property can be provided, and must be of type `enum`.

- the `time_quantum` is the minimum amount of time, in seconds, that is meaningful for an agent; context updates occurring faster than this quantum won't be taken into account.

#### Context properties types ####

##### Base types: `enum` and `continuous` #####

`enum` and `continuous` are the two base **craft ai** types:

- `enum` properties can take any string values;
- `continuous` properties can take any real number value.

##### Time types: `timezone`, `time_of_day` and `day_of_week` #####

**craft ai** defines 3 types related to time:

- `time_of_day` properties can take any real number belonging to **[0.0; 24.0[**
representing the number of hours in the day since midnight (e.g. 13.5 means
13:30),
- `day_of_week` properties can take any integer belonging to **[0, 6]**, each
value represents a day of the week starting from Monday (0 is Monday, 6 is
Sunday).
- `timezone` properties can take string values representing the timezone as an
offset from UTC, the expected format is **Â±[hh]:[mm]** where `hh` represent the
hour and `mm` the minutes from UTC (eg. `+01:30`)), between `-12:00` and
`+14:00`.

> :information_source: By default, the values of the `time_of_day` and `day_of_week`
> properties are generated from the [`timestamp`](#timestamp) of an agent's
> state and the agent's current `timezone`. Therefore, whenever you use generated
> `time_of_day` and/or `day_of_week` in your model, you **must** provide a
> `timezone` value in the context.
>
> If you wish to provide their values manually, add `is_generated: false` to the
> time types properties in your model. In this case, since you provide the values, the
> `timezone` property is not required, and you must update the context whenever
> one of these time values changes in a way that is significant for your system.

##### Examples #####

Let's take a look at the following model. It is designed to model the **color**
of a lightbulb (the `lightbulbColor` property, defined as an output) depending
on the **outside light intensity** (the `lightIntensity` property), the **time
of the day** (the `time` property) and the **day of the week** (the `day`
property).

`day` and `time` values will be generated automatically, hence the need for
`tz`, the current Time Zone, to compute their value from given
[`timestamps`](#timestamp).

The `time_quantum` is set to 100 seconds, which means that if the lightbulb
color is changed from red to blue then from blue to purple in less that 1
minutes and 40 seconds, only the change from red to purple will be taken into
account.

```json
{
  "context": {
      "lightIntensity":  {
        "type": "continuous"
      },
      "time": {
        "type": "time_of_day"
      },
      "day": {
        "type": "day_of_week"
      },
      "tz": {
        "type": "timezone"
      },
      "lightbulbColor": {
          "type": "enum"
      }
  },
  "output": ["lightbulbColor"],
  "time_quantum": 100
}
```

In this second examples, the `time` property is not generated, no property of
type `timezone` is therefore needed. However values of `time` must be manually
provided continuously.

```json
{
  "context": {
    "time": {
      "type": "time_of_day",
      "is_generated": false
    },
    "lightIntensity":  {
        "type": "continuous"
    },
    "lightbulbColor": {
        "type": "enum"
    }
  },
  "output": ["lightbulbColor"],
  "time_quantum": 100
}
```

### Timestamp ###

**craft ai** API heavily relies on `timestamps`. A `timestamp` is an instant represented as a [Unix time](https://en.wikipedia.org/wiki/Unix_time), that is to say the amount of seconds elapsed since Thursday, 1 January 1970 at midnight UTC. In most programming languages this representation is easy to retrieve, you can refer to [**this page**](https://github.com/techgaun/unix-time/blob/master/README.md) to find out how.

The `craftai.time.Time` class facilitates the handling of time types in **craft ai**. It is able to extract the different **craft ai** formats from various _datetime_ representations, thanks to [datetime](https://docs.python.org/3.5/library/datetime.html).

```python
from craftai.time import Time

# From a unix timestamp and an explicit UTC offset
t1 = Time(1465496929, '+10:00')

# t1 == {
#   utc: '2016-06-09T18:28:49.000Z',
#   timestamp: 1465496929,
#   day_of_week: 4,
#   time_of_day: 4.480277777777778,
#   timezone: '+10:00'
# }

# From a unix timestamp and using the local UTC offset.
t2 = Time(1465496929)

# Value are valid if in Paris !
# t2 == {
#   utc: '2016-06-09T18:28:49.000Z',
#   timestamp: 1465496929,
#   day_of_week: 3,
#   time_of_day: 20.480277777777776,
#   timezone: '+02:00'
# }

# From a ISO 8601 string. Note that here it should not have any ':' in the timezone part
t3 = Time('1977-04-22T01:00:00-0500')

# t3 == {
#   utc: '1977-04-22T06:00:00.000Z',
#   timestamp: 230536800,
#   day_of_week: 4,
#   time_of_day: 1,
#   timezone: '-05:00'
# }

# Retrieve the current time with the local UTC offset
now = Time()

# Retrieve the current time with the given UTC offset
nowP5 = Time(tz='+05:00')
```

### Agent ###

#### Create ####

Create a new agent, and create its [model](#model).

```python
client.create_agent(
    { # The model
        "context": {
            "presence": {
                "type": 'enum'
            },
            "lightIntensity": {
                "type": 'continuous'
            },
            "lightbulbColor": {
                "type": 'enum'
            }
        },
        "output": ['lightbulbColor'],
        "time_quantum": 100
    },
    "aphasic_parrot" # id for the agent, if undefined a random id is generated
)
```

#### Delete ####

```python
client.delete_agent(
    "aphasic_parrot" # The agent id
)
```

#### Retrieve ####

```python
client.get_agent(
    "aphasic_parrot" # The agent id
)
```

#### List ####





### Context ###

#### Add operations ####

```python
client.add_operations(
    "aphasic_parrot", # The agent id
    [ # The list of context operations
        {
            "timestamp": 1464600000,
            "diff": {
                "presence": "robert",
                "lightIntensity": 0.4,
                "lightbulbColor": "green"
            },
        },
        {
            "timestamp": 1464600500,
            "diff": {
                "presence": "gisele",
                "lightbulbColor": "purple"
                },
        },
        {
            "timestamp": 1464602400,
            "diff": {
                "presence": "gisele+robert",
                "lightbulbColor": "purple"
            }
        },
        {
            "timestamp": 1464635400,
            "diff": {
                "presence": "gisele+robert",
                "lightbulbColor": "red"
            }
        },
        {
            "timestamp": 1464722520,
            "diff": {
                "presence": "gisele+robert",
                "lightbulbColor": "red"
            }
        },
        {
            "timestamp": 1464732520,
            "diff": {
                "presence": "gisele+robert",
                "lightbulbColor": "orange"
            }
        },
        {
            "timestamp": 1464752520,
            "diff": {
                "presence": "gisele+robert",
                "lightIntensity": 0.2,
                "lightbulbColor": "orange"
            }
        }
    ]
)
```

#### List operations ####

```python
client.get_operations_list(
    "aphasic_parrot" # The agent id
)
```

#### Retrieve state ####

```python
client.get_context_state(
    "aphasic_parrot", # The agent id
    1464600256 # The timestamp at which the context state is retrieved
)
```

### Decision tree ###

Decision trees are computed at specific timestamps, directly by **craft ai** which learns from the context operations [added](#add-operations) throughout time.

When you [compute](#compute) a decision tree, **craft ai** should always return you an array containing the **tree version** as the first element. This **tree version** determines what other information is included in the response body.

In version `"0.0.3"`, the other included elements are (in order):

- the agent's model as specified during the agent's [creation](#create-agent)
- the tree itself as a JSON object:
  
  * Internal nodes are represented by a `"predicate_property"` and a `"children"` array. The latter contains the actual two children of the current node and the criterion (`"predicate"`) on the `"predicate_property"`'s value, to decide which child to walk down towards.
  * Leaves have an output `"value"` and a confidence for this value, instead of a `"predicate_property"` and a `"children"` array.
  * The root has one more key than regular nodes: the `"output_property"` which defines what is the actual meaning of the leaves' value.

#### Compute ####

```python
client.get_decision_tree(
    "aphasic_parrot", # The agent id
    1464810471 # The timestamp at which the decision tree is retrieved
)
```

#### Take Decision ####

To get a chance to store and reuse the decision tree, use `get_decision_tree` and use `decide`, a simple function evaluating a decision tree offline.

```python
tree = { ... } # Decision tree as retrieved through the craft ai REST API

# Compute the decision on a fully described context
decision = client.decide(
    tree,
    {
        "presence": 'gisele',
        "lightIntensity": 0.75,
    }
)
```

The computed decision looks like:

```python
{
    "context": { # The context in which the decision was taken
        "lightIntensity": 0.75,
        "presence": "gisele"
    },
    "predicates": [ # The ordered list of predicates that were validated to reach this decision
        {
            "op": "continuous.greaterthanorequal",
            "value": 0.4000000059604645,
            "property": "lightIntensity"
        },
        {
            "op": "enum.equal",
            "value": "gisele",
            "property": "presence"
        }
    ],
    "confidence": 0.9755546450614929 # The confidence in the decision
    "decision": { # The decision itself
        "lightbulbColor": "purple"
    }
}
```

### Error Handling ###

When using this client, you should be careful wrapping calls to the API with `try/except` blocks, in accordance with the [EAFP](https://docs.python.org/3/glossary.html#term-eafp) principle.

The **craft ai** python client has its specific exception types, all of them inheriting from the `CraftAIError` type.

All methods which have to send an http request (all of them except `decide`) may raise either of these exceptions: `CraftAINotFoundError`, `CraftAIBadRequestError`, `CraftAICredentialsError` or `CraftAIUnknownError`.
The `decide`Â method should only raise `CrafAIDecisionError` type of exceptions.
