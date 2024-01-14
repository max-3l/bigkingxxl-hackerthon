<template>
  <div v-if="showInput" class="input horizontal-cards">
    <q-form @submit="submitPrompt" class="full-card">
      <q-input rounded outlined v-model="prompt" label="Prompt" class="full-card" />
    </q-form>
    <q-select rounded outlined v-model="model" :options="models" label="Model" class="third-card" />
  </div>
  <div v-show="!showInput" class="card">
    <q-card class="bottom-space">
      <q-card-section>
        <q-card-title>
          <div class="no-spacing prompt-header">
            <strong class="header-label">🙋 Your Prompt</strong>
            <div class="no-spacing" @click="selectModel">
              <strong> {{ model }} </strong>
            </div>
          </div>
        </q-card-title>
        <q-card-main>
          {{ prompt }}
        </q-card-main>
      </q-card-section>
    </q-card>
    <!-- DIV to align two cards horizontally -->
    <div class="horizontal-cards">
      <div class="vertical-cards">
        <q-card class="full-card" flat>
          <q-card-section>
            <q-card-title>
              <strong class="header-label">🥴 Insights</strong> <br>
            </q-card-title>
            <q-card-main>
              <strong>Expertise</strong> <br>
              <template v-for="model in model_expertise" v-bind:key="model.model">
                <div class="no-spacing">
                  {{ model.model }} - {{ (model.expertise * 100).toFixed(2) }}%
                  <!-- SVG that plots a confidence score between 0 and 1 as a bar. Uses confidence property.-->
                  <svg class="full-card svg">
                    <rect x="1" y="1" rx="1%" width="99%" height="15"
                      style="fill:rgb(255,255,255);stroke-width:1;stroke:rgb(0,0,0)" />
                    <rect x="2" y="2" rx="1%" :width="model.expertise * 99 + '%'" height="13"
                      :style="'fill:' + expertiseColor(model.expertise) + ';stroke-width:0;stroke:rgb(0,0,0)'" />
                  </svg>
                </div>
              </template>
              <strong>Annotations</strong> <br>
              <q-chip v-for="annotation in annotations" :key="annotation.index" clickable
                :outline="showAnnotationExplanation == annotation.index" :label="annotation.keyword"
                :color="annotationColor(annotation)"
                @click="showAnnotationExplanation = showAnnotationExplanation == annotation.index ? -1 : annotation.index" />
              <div class="top-space" v-if="showAnnotationExplanation != -1">
                <strong>Annotation Details</strong> <br>
                {{ annotationExplanation }}
                <div class="thumbs">
                  <q-btn flat @click="thumbsUp">👍</q-btn>
                  <q-btn flat @click="thumbsDown">👎</q-btn>
                </div>
              </div>
            </q-card-main>
          </q-card-section>
        </q-card>
      </div>

      <q-card flat class="full-card">
        <q-card-section>
          <q-card-title>
            <div class="no-spacing horizontal-cards">
              <strong class="header-label">🤖 AI Response</strong>
              <div class="no-spacing">
                Confidence - {{ (confidence * 100).toFixed(2) }}%
                <!-- SVG that plots a confidence score between 0 and 1 as a bar. Uses confidence property.-->
                <svg class="full-card svg">
                  <rect x="1" y="1" rx="1%" width="99%" height="15"
                    style="fill:rgb(255,255,255);stroke-width:1;stroke:rgb(0,0,0)" />
                  <rect x="2" y="2" rx="1%" :width="confidence * 99 + '%'" height="13"
                    :style="'fill:' + confidenceColor + ';stroke-width:0;stroke:rgb(0,0,0)'" />
                </svg>
              </div>
            </div>
          </q-card-title>
          <q-card-main>
            {{ response }}
            <q-form v-show="done && !annotationSubmitted" @submit="submitAnnotation" class="horizontal-cards top-space">
              <q-input filled v-model="customAnnotation" label="Your annotation" dense class="full-width">
              </q-input>
              <q-btn dense flat icon="send" type="submit" />
            </q-form>
          </q-card-main>
        </q-card-section>
      </q-card>
    </div>
  </div>
</template>

<script lang="ts">
import {
  defineComponent,
  ref,
  reactive,
} from 'vue';
import * as chroma from 'chroma-js';

interface Annotation {
  annotation: string;
  keyword: string;
  sentiment: number;
  index: number;
  num_votes: number;
}

interface ModelExpertise {
  model: string;
  expertise: number;
}

const models = {
  'gpt-3.5-turbo-1106': 'Chat GPT 3.5 (latest)',
  'gpt-3.5-turbo': 'Chat GPT 3.5',
  'gpt-4': 'Chat GPT 4'
}

export default defineComponent({
  name: 'ExampleComponent',
  props: {
    title: {
      type: String,
      required: true
    },
    active: {
      type: Boolean
    }
  },
  setup() {
    return {
      prompt: ref(''),
      response: ref(''),
      confidence: ref(0.0),
      showInput: ref(true),
      confidenceColor: ref('#000000'),
      showAnnotationExplanation: ref(-1),
      model: ref('gpt-3.5-turbo-1106'),
      models: ref(Object.keys(models)),
      done: ref(false),
      annotationSubmitted: ref(false),
      customAnnotation: ref(''),
      queryId: ref(-1),
      annotations: reactive<Annotation[]>([]),
      model_expertise: reactive<ModelExpertise[]>([])
    };
  },
  computed: {
    annotationExplanation(): string {
      if (this.showAnnotationExplanation == -1) {
        return ''
      }
      const annotation = this.annotations.filter((annotation: Annotation) => annotation.index == this.showAnnotationExplanation)[0]
      return annotation.annotation
    }
  },
  watch: {
    model() {
      this.showAnnotationExplanation = -1
      this.response = ''
      this.confidence = 0.0
      this.showInput = true
      this.confidenceColor = '#000000'
      this.done = false
      this.annotationSubmitted = false
      this.customAnnotation = ''
      this.queryId = -1
      this.annotations = []
      this.model_expertise = []
    }
  },
  methods: {
    async submitAnnotation(e: Event) {
      console.log('submit annotation')
      e.preventDefault();
      if (this.customAnnotation == '') {
        console.log('no annotation')
        return
      }
      console.log('submit annotation')
      const response = await fetch('http://localhost:8000/add_annotation', {
        method: 'POST', // *GET, POST, PUT, DELETE, etc.)
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query_id: this.queryId,
          annotation: this.customAnnotation
        }),
      })
      if (!response.ok) {
        console.log('not ok')
        return;
      }
      if (!response.body) {
        console.log('no body')
        return;
      }
      const annotation = (await response.json())
      this.annotations.push(annotation)
      this.annotationSubmitted = true
    },
    async queryAnnotations() {
      const response = await fetch(`http://localhost:8000/query_annotation/${this.queryId}`)
      if (!response.ok) {
        console.log('not ok')
        return;
      }
      if (!response.body) {
        console.log('no body')
        return;
      }
      const annotations = (await response.json())
      this.annotations.push(...annotations)
    },
    expertiseColor(expertise: number): string {
      const f = chroma.scale(['red', '#c9b23c', 'green'])
      return f(expertise).hex()
    },
    async getModelExpertise() {
      const response = await fetch(`http://localhost:8000/get_expertise_models/${this.queryId}`)
      if (!response.ok) {
        console.log('not ok')
        return
      }
      if (!response.body) {
        console.log('no body')
        return
      }
      const modelExpertise = (await response.json())
      this.model_expertise.push(...modelExpertise)
    },
    selectModel() {
      this.$q.dialog({
        title: 'Select Model',
        message: 'Select a model to use for the response.',
        options: {
          type: 'radio',
          model: this.model,
          items: Object.entries(models).map(([model, label]) => {
            return { label: label, value: model }
          })
        },
        cancel: true,
        persistent: true
      }).onOk((model: string) => {
        this.model = model;
      });
      console.log('select model');
    },
    submitPrompt(e: Event) {
      e.preventDefault();
      console.log(this.prompt);
      this.showInput = false;
      this.sendRequest();
    },
    thumbsUp() {
      if (this.showAnnotationExplanation == -1) {
        return
      }
      fetch(`http://localhost:8000/upvote/${this.showAnnotationExplanation}`, {
        method: 'POST', // *GET, POST, PUT, DELETE, etc.)
      })
    },
    thumbsDown() {
      if (this.showAnnotationExplanation == -1) {
        return
      }
      fetch(`http://localhost:8000/downvote/${this.showAnnotationExplanation}`, {
        method: 'POST', // *GET, POST, PUT, DELETE, etc.)
      })
    },
    async animateConfidence(confidence: number) {
      const f = chroma.scale(['red', '#c9b23c', 'green'])
      this.confidence = 0
      const interval = setInterval(() => {
        this.confidence = this.confidence + 0.01
        this.confidenceColor = f(this.confidence).hex()
        if (this.confidence >= confidence) {
          clearInterval(interval)
        }
      }, 5);
    },
    annotationColor(annotation: Annotation): string {
      if (annotation.sentiment == 1) {
        return 'green'
      }
      if (annotation.sentiment == -1) {
        return 'red'
      }
      return 'yellow'
    },
    async sendRequest() {
      const query = await fetch(`http://localhost:8000/query/${this.model}`, {
        method: 'POST', // *GET, POST, PUT, DELETE, etc.)
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query: this.prompt
        }),
      })
      if (!query.ok) {
        console.log('not ok')
        return;
      }
      if (!query.body) {
        console.log('no body')
        return;
      }
      const queryId = (await query.json())['queryId']
      this.queryId = queryId
      const stream = await fetch(`http://localhost:8000/query/${queryId}/response`)
      if (!stream.body) {
        console.log('no body')
        return;
      }
      const reader = stream.body.pipeThrough(new TextDecoderStream()).getReader()
      let done = false
      while (!done) {
        const { value, done: done2 } = await reader.read()
        if (done2) {
          done = true
          this.done = true
          break
        }
        this.response = this.response + value.toString()
      }
      const confidenceResponse = await fetch(`http://localhost:8000/query/${queryId}/confidence`)
      if (!confidenceResponse.body) {
        console.log('no body')
        return;
      }
      await this.getModelExpertise()
      await this.queryAnnotations()
      const confidence = (await confidenceResponse.json())['confidence']
      this.animateConfidence(confidence.toFixed(2))
    }
  }
});
</script>

<style>
.input {
  width: 90%
}

.card {
  width: 90%
}

.auto-width {
  width: auto;
}

.full-card {
  width: 100%;
}

.third-card {
  width: 33%;
}

.bottom-space {
  margin-bottom: 10px;
}

.top-space {
  margin-top: 10px;
}

.some-padding {
  padding: 10px;
}

.horizontal-cards {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  gap: 10px;
}

.svg {
  height: 20px;
}

.no-spacing {
  margin: 0px;
  padding: 0px;
}

.prompt-header {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}

.header-label {
  font-size: 20px;
}
</style>
